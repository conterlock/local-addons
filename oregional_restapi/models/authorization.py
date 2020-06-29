# -*- coding: utf-8 -*-
# 1 : imports of python lib
import datetime
import logging
import random
import string

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models, tools  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations:
_logger = logging.getLogger(__name__)


# Class
class OregionalRestapiAuthorization(models.Model):
    # Private attributes
    _name = 'oregional.restapi.authorization'
    _description = "REST API authorization"

    # Default methods

    # Field declarations
    access_token = fields.Char(
        string="Access Token",
    )
    access_token_expiry = fields.Datetime(
        string="Access Token Expiry",
    )
    application = fields.Many2one(
        comodel_name='oregional.restapi.application',
        help="The remote application for which the access is granted",
        index=True,
        ondelete='cascade',
        string="Application",
    )
    authorization_uri = fields.One2many(
        comodel_name='oregional.restapi.authorization.uri',
        inverse_name='authorization',
        help="URI of the remote application for which the access is granted",
        index=True,
        string="Application URI",
    )
    user_id = fields.Char(
        help="Identifier for the user in the remote application",
        required=True,
        string="User ID",
    )
    user_secret = fields.Char(
        help="Secret for the user in the remote application",
        required=True,
        string="User Secret"
    )
    refresh_token = fields.Char(
        string="Refresh Token",
    )
    refresh_token_expiry = fields.Datetime(
        string="Refresh Token Expiry",
    )
    user = fields.Many2one(
        comodel_name='res.users',
        help="Linked Odoo user",
        index=True,
        string="User",
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides
    # # Override name_get
    @api.multi
    def name_get(self):
        # Initialize result
        result = []

        # Iterate through self
        for item in self:
            # Set name from application and the name of the user
            name = item.application.display_name + " - " + item.user.display_name

            # Append to list
            result.append((item.id, name))

        # Return
        return result

    # Action methods
    # # Revoke token for an authorization
    @api.multi
    def action_revoke_tokens(self):
        if self._context.get('active_ids'):
            ids = self._context.get('active_ids')
        else:
            ids = [self.id]

        authorizations = self.env['oregional.restapi.authorization'].search([
            ('id', 'in', ids)
        ])

        for authorization in authorizations:
            # Revoke tokens
            authorization.access_token = False
            authorization.access_token_expiry = False
            authorization.refresh_token = False
            authorization.refresh_token_expiry = False

    # Business methods
    @api.model
    def _generate_user_id(self):
        """ Generate a user_id"""
        return self._get_token()

    @api.model
    def _generate_user_secret(self):
        """ Generate a user_secret"""
        return self._get_token()

    @api.model
    def _get_token(self):
        """ Get a random token (32 characters mixed with uppercase, lowercase and digits)"""
        # Initialize token
        new_token = ''

        # Iterate for random characters
        for i in range(32):
            new_token += random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)

        # Return
        return new_token

    @api.model
    def is_valid_refresh_token(self, refresh_token):
        """ Check if a refresh token is valid

        :param code: a string considered to be a refresh token

        :returns true or false

        """
        # Get linked authorization
        authorization = self.env['oregional.restapi.authorization'].search([
            ('refresh_token', '=', refresh_token)
        ])

        # If only one authorization found
        if authorization and len(authorization) == 1:
            # Application refresh token expiry setting = 0, so it never expires
            if authorization.application.refresh_token_expiry == 0:
                return True
            # Application refresh token expiry setting > 0, so it can expire
            elif authorization.refresh_token_expiry:
                if authorization.refresh_token_expiry > fields.Datetime.now():
                    return True
                else:
                    return False
            # Application refresh token expiry is changed from 0 to something and there is already a refresh token
            elif authorization.refresh_token and not authorization.refresh_token_expiry:
                return True
            # All other cases
            else:
                return False
        # If no or more than one authorization found
        else:
            return False

    @api.model
    def get_access_token_response_data_from_authorization_code(self, code):
        """ Get access token data

        :param code: a string considered to be an authorization code

        :returns dictionary of access token data or false
        """
        # Result
        if self.env['oregional.restapi.authorization.code'].is_valid_authorization_code(code):
            # Write
            restapi_authorization_code = self.env['oregional.restapi.authorization.code'].search([
                ('code', '=', code)
            ])
            if len(restapi_authorization_code) == 1:
                # Expiry seconds
                access_token_exp_sec = restapi_authorization_code.authorization.application.access_token_expiry or 3600
                refresh_token_exp_sec = restapi_authorization_code.authorization.application.refresh_token_expiry or 0

                # Result
                result = self._generate_access_token_response_data("Bearer", access_token_exp_sec)

                # Set access token expiry
                access_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=access_token_exp_sec)

                # Set refresh token expiry
                if refresh_token_exp_sec == 0:
                    refresh_token_expiry = False
                else:
                    refresh_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=refresh_token_exp_sec)

                # Write
                restapi_authorization_code.authorization.write({
                    'access_token': result['access_token'],
                    'access_token_expiry': access_token_expiry,
                    'refresh_token': result['refresh_token'],
                    'refresh_token_expiry': refresh_token_expiry
                })

            else:
                result = False
        else:
            result = False

        # Return
        return result

    @api.model
    def get_access_token_response_data_from_refresh_token(self, refresh_token):
        """ Get access token data from a refresh token

        :param refresh_token: a string that is considered to be a refresh token

        :returns dictionary of access token data or false
        """
        # Check if refresh_token is valid
        is_valid_refresh_token = self.env['oregional.restapi.authorization'].is_valid_refresh_token(refresh_token)

        if is_valid_refresh_token:
            authorization = self.env['oregional.restapi.authorization'].search([
                ('refresh_token', '=', refresh_token)
            ])

            if len(authorization) == 1:
                # Expiry seconds
                access_token_exp_sec = authorization.application.access_token_expiry or 3600
                refresh_token_exp_sec = authorization.application.refresh_token_expiry or 0

                # Result
                result = self._generate_access_token_response_data("Bearer", access_token_exp_sec)

                # Set access token expiry
                access_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=access_token_exp_sec)

                # Set refresh token expiry
                if refresh_token_exp_sec == 0:
                    refresh_token_expiry = False
                else:
                    refresh_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=refresh_token_exp_sec)

                # Write
                authorization.write({
                    'access_token': result['access_token'],
                    'access_token_expiry': access_token_expiry,
                    'refresh_token': result['refresh_token'],
                    'refresh_token_expiry': refresh_token_expiry
                })

            else:
                result = False
        else:
            result = False

        # Return
        return result

    @api.model
    def _generate_access_token_response_data(self, token_type, expiry):
        """ Generate access token data

        :param token_type: string for the token type (eg: Bearer)

        :param expiry: seconds as integer

        :returns oregional.restapi.authorization object

        """
        # Generate tokens
        new_access_token = self._get_token()
        new_refresh_token = self._get_token()

        # Result
        result = {
            'access_token': new_access_token,
            'token_type': token_type,
            'expires_in': expiry,
            'refresh_token': new_refresh_token
        }

        # Return
        return result

    def get_valid_authorization_from_request(self, request):
        """ Get valid authorization from a http request

        For simplicity we pass the entire request and get the header information here

        :param request: http request

        :returns oregional.restapi.authorization object
        """
        request_header_access_token = self.get_access_token_from_request_authorization_header(request)

        if request_header_access_token:
            # Get odoo access token info
            authorization = self.env['oregional.restapi.authorization'].search([
                ('access_token', '=', request_header_access_token)
            ])

            if not authorization or authorization.access_token_expiry < fields.Datetime.now():
                return False
            else:
                return authorization

    def get_access_token_from_request_authorization_header(self, request):
        """ Get access token from the authorization header of a request

        :param: request: http request

        :returns: access token string or false
        """
        # Search for authorization in the request header
        if request.httprequest.headers.get('Authorization'):
            authorization_header = request.httprequest.headers.get('Authorization')

            # If type is Bearer, than get the token
            if 'Bearer' in authorization_header:
                result = request.httprequest.headers.get('Authorization').split(' ')[1]

                return result
            else:
                return False
        else:
            return False

    def get_user_authorization(self, application, user, uri=False):
        """ Get application authorization for a user

            :param: application: the authorized application

            :param: user : the user who authorized the application

            :param: uri: an URI that must be individually authorized for the application

            :returns: oregional.restapi.authorization.code object
        """
        # Set internal variable
        create_authorization = False
        create_uri_authorization = False
        valid_uri = False

        # Search for existing authorization
        authorization = self.env['oregional.restapi.authorization'].sudo().search([
            ('application', '=', application.id),
            ('user', '=', user.id)
        ])

        if not authorization:
            create_authorization = True

        # Double check uri
        if uri:
            # Get uri from application uris
            application_uri = self.env['oregional.restapi.application.uri'].sudo().search([
                ('application', '=', application.id),
                ('uri', '=', uri)
            ])

            if len(application_uri) == 1:
                valid_uri = True

            # If valid uri and it needs individual authorization
            if valid_uri and application_uri.authorize_individually:
                uri_authorization = self.env['oregional.restapi.authorization.uri'].sudo().search([
                    ('authorization', '=', authorization.id),
                    ('uri', '=', uri),
                ])

                if not uri_authorization:
                    create_uri_authorization = True

        # Create when necessary
        if create_authorization:
            # Create user_id for the user
            user_id = self._generate_user_id()

            # Create user_secret for the user
            user_secret = self._generate_user_secret()

            # Create new authorization
            authorization = self.sudo().create({
                'application': application.id,
                'user_id': user_id,
                'user_secret': user_secret,
                'user': user.id
            })

        # Add uri when necessary
        if create_uri_authorization:
            self.env['oregional.restapi.authorization.uri'].sudo().create({
                'authorization': authorization.id,
                'uri': uri,
            })

        # Return
        return authorization
