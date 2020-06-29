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
class OregionalRestapiAuthorizationCode(models.Model):
    # Private attributes
    _name = 'oregional.restapi.authorization.code'
    _description = "REST API authorization code"

    # Default methods

    # Field declarations
    active = fields.Boolean(
        default=True,
        readonly=True,
        string="Active",
        track_visibility='onchange',
    )
    authorization = fields.Many2one(
        comodel_name='oregional.restapi.authorization',
        help="The remote application for which the user grants access",
        index=True,
        ondelete='cascade',
        readonly=True,
        string="Authorization",
    )
    code = fields.Char(
        readonly=True,
        string="Authorization Code",
    )
    expiry = fields.Datetime(
        readonly=True,
        string="Expiry",
    )
    used_at = fields.Datetime(
        readonly=True,
        string="Used At",
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
            # Set name to uri name
            name = item.id

            # Append to list
            result.append((item.id, name))

        # Return
        return result

    # Action methods
    @api.multi
    def action_revoke_authorization_codes(self):
        """ Action to revoke authorization codes"""
        if self._context.get('active_ids'):
            ids = self._context.get('active_ids')
        else:
            ids = [self.id]

        authorization_codes = self.env['oregional.restapi.authorization.code'].search([
            ('id', 'in', ids)
        ])

        for authorization_code in authorization_codes:
            # Revoke
            authorization_code.revoke_existing_codes(authorization_code.authorization)

        # Return
        return

    # Business methods
    @api.model
    def get_authorization_code(self, authorization):
        """ Get a code for an authorization

            :param authorization

            :returns code
        """
        # Check a few things
        if not authorization.application:
            return False

        if not authorization.user:
            return False

        # Get application authorization code expiry setting
        if authorization.application.authorization_code_expiry:
            expiry_seconds = authorization.application.authorization_code_expiry
        else:
            expiry_seconds = 600

        # Set authorization code expiry
        expiry = datetime.datetime.now() + datetime.timedelta(seconds=expiry_seconds)

        # Revoke existing authorization codes
        self.sudo().revoke_existing_codes(authorization)

        # Get new code
        code = self._generate_authorization_code()

        # Create authorization code
        code = self.env['oregional.restapi.authorization.code'].sudo().create({
            'authorization': authorization.id,
            'code': code,
            'expiry': expiry
        })

        return code

    @api.model
    def _generate_authorization_code(self):
        """ Generate an authorization code

            :returns: string (random 32 characters, mix of uppercase, lowercase and digits)
        """
        code = ''

        for i in range(32):
            code += random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)

        return code

    @api.model
    def is_valid_authorization_code(self, code):
        """ Check if an authorization code is valid"""
        valid_code = self.env['oregional.restapi.authorization.code'].search([
            ('active', '=', True),
            ('code', '=', code),
        ])

        if valid_code and valid_code.expiry > fields.Datetime.now():
            return True
        else:
            return False

    @api.model
    def is_valid_application_authorization_code(self, application, code):
        """ Validate an authorization code for an application"""
        valid_code = self.env['oregional.restapi.authorization.code'].search([
            ('code', '=', code)
        ])
        _logger.debug("is_valid_application_authorization_code ARGS")
        _logger.debug(application)
        _logger.debug(valid_code)

        if len(valid_code) == 1 and valid_code.authorization.application == application:
            return True
        else:
            return False

    @api.model
    def use_code(self):
        """ A valid authorization code is used by a process (eg: access_token request) for validation"""
        # Set used_at timestamp
        self.sudo().write({
            'used_at': fields.datetime.now()
        })

        # Revoke code
        self.revoke_code()

        # Return
        return

    @api.model
    def revoke_code(self):
        """ Revoke an authorization code """
        # Ensure one
        self.ensure_one()

        # Get application authorization code retain setting
        if self.authorization.application.authorization_code_retain > 0:
            deactivate = True
        else:
            deactivate = False

        # Do revoke
        if deactivate:
            self.deactivate_authorization_code()
        else:
            self.delete_authorization_code()

        # Return
        return

    @api.model
    def revoke_existing_codes(self, authorization):
        """ Revoke authorization codes for an authorization

        If authorization code retain setting is greater than 0 days, than deactivate, otherwise delete the codes

        :param: authorization : the authorization for which the codes should be deactivated

        :returns True
        """
        # Search
        codes = self.env['oregional.restapi.authorization.code'].sudo().search([
            ('authorization', '=', authorization.id)
        ])

        # Revoke
        for code in codes:
            code.revoke_code()

        # Return
        return

    @api.model
    def deactivate_authorization_code(self):
        """ Deactivate an authorization code"""
        self.ensure_one()

        self.sudo().write({
            'active': False
        })

        return

    @api.model
    def deactivate_authorization_code(self):
        """ Deactivate an authorization code"""
        # Ensure one
        self.ensure_one()

        # Write
        self.write({
            'active': False
        })

        # Return
        return

    @api.model
    def deactivate_all_authorization_codes(self):
        """ Deactivate all authorization codes"""
        # Search and deactivate
        for item in self.env['oregional.restapi.authorization.code'].search([]):
            item.deactivate_authorization_code()

        # Return
        return

    @api.model
    def delete_authorization_code(self):
        """ Delete an authorization code"""
        # Ensure one
        self.ensure_one()

        # Delete
        self.unlink()

        # Return
        return

    @api.model
    def delete_all_authorization_codes(self):
        """ Delete all authorization codes"""
        # Search and delete
        for item in self.env['oregional.restapi.authorization.code'].search([]):
            item.delete_authorization_code()

        # Return
        return
