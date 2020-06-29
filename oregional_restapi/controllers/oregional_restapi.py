# -*- coding: utf-8 -*-
# 1 : imports of python lib
import json
import logging
import urllib
import werkzeug

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, http, models, tools
from odoo.http import request
from odoo.http import Response
from odoo.service import common as OdooServiceCommon

# 3 : imports from odoo modules

# 4 : variable declarations
_logger = logging.getLogger(__name__)


# Class
class OregionalRestApiBase(http.Controller):

    @http.route(['/orestapi/version'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_version(self, **request_data):
        """ Get the version of the database and the orestapi app without authentication"""
        version = {}

        # Get database version
        db_version = OdooServiceCommon.exp_version()

        # Get app version
        ir_module_module_obj = request.env['ir.module.module'].sudo()
        orestapi_app = ir_module_module_obj.search([('name', '=', 'oregional_restapi')])
        app_version = {
            'orestapi_version': orestapi_app.installed_version
        }

        # Update version dict
        version.update(db_version)
        version.update(app_version)

        # Assemble response
        response_code = 200
        response_data = version

        # Return
        return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/application/status'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_application_status(self, **request_data):
        """Get current status of an application

        :param request_data: data of the https request

        :returns dictionary of ir.model.model with model and name
        """
        # Get application based on authorization from request_data
        application = request.env['oregional.restapi.application'].sudo()\
            .do_client_basic_access_authentication(request)

        if not application:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationData-0010",
                'orestapi_message': _("No application found for provided basic access authentication")
            }
            return self._get_response_object(response_code, response_data)
        else:
            # Update request_data
            request_data.update(request.httprequest.data or {})

            # Get application object
            orestapi_app_obj = request.env['oregional.restapi.application'].sudo()

            # Search for application
            application = orestapi_app_obj.search([
                ('id', '=', application.id)
            ])
            self._write_to_debug_log("application status application", application)

            # Search again for archived applications
            if not application:
                archived_application = orestapi_app_obj.search([
                    ('active', '=', False),
                    ('id', '=', application.id)
                ])
                self._write_to_debug_log("application status archived_application", archived_application)

            # Prepare list of fields to return for the read operation
            field_list = ['id', 'active', 'display_name', 'company']

            # Assemble response
            if application and len(application) == 1:
                response_code = 200
                response_data = application.read(field_list)
                self._write_to_debug_log("application status response_data", response_data)
            elif application and archived_application:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiApplicationData-0020",
                    'orestapi_message': _("Application configuration error in Odoo! Contact Odoo administrator!")
                }
            elif archived_application and len(archived_application) == 1:
                response_code = 200
                response_data = archived_application.read(field_list)
                self._write_to_debug_log("application status response_data", response_data)
            else:
                response_code = 200
                response_data = {
                    'orestapi_code': "OrestapiApplicationData-0030",
                    'orestapi_message': _("Not found")
                }

            # Return
            return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/application/model'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_application_model(self, **request_data):
        """Get a dictionary of available models based on application settings and user permissions

        :param request_data: data of the https request

        :returns dictionary of ir.model.model with model and name
        """
        # Get authorization from request_data
        authorization = request.env['oregional.restapi.authorization'].sudo()\
            .get_valid_authorization_from_request(request)

        if not authorization:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationGetModel-0010",
                'orestapi_message': _("Not authorized")
            }
            return self._get_response_object(response_code, response_data)
        else:
            # Update request_data
            request_data.update(request.httprequest.data or {})

            # Get available models
            orestapi_app_obj = request.env['oregional.restapi.application'].sudo()

            application = orestapi_app_obj.search([
                ('id', '=', authorization.application.id)
            ])
            self._write_to_debug_log("application model application", application)
            self._write_to_debug_log("application model application", application)

            # Assemble return dictionary
            if application.model_scheme:
                allowed_model_list = application.model_scheme.get_allowed_models()
                permitted_model_list = []
                for allowed_model_list_item in allowed_model_list:
                    if application.model_scheme.can_user_read_model(authorization.user, allowed_model_list_item[0].model):
                        self._write_to_debug_log("application model allowed_model[0]", allowed_model_list_item)
                        permitted_model_list.append(allowed_model_list_item)
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiApplicationGetModel-0020",
                    'orestapi_message': _("Invalid model scheme settings. Please contact an Odoo administrator.")
                }
                return self._get_response_object(response_code, response_data)

            # Assemble response
            self._write_to_debug_log("application model permitted_model_list", permitted_model_list)
            response_model_list = []
            for model in permitted_model_list:
                model_data = {
                    'model': model[0].model,
                    'name': model[1]
                }
                response_model_list.append(model_data)

            # Return result
            response_code = 200
            response_data = response_model_list
            return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/application/user'], type="http", auth="user", csrf=False, website=True)
    def oregional_restapi_application_user(self, **request_data):
        """ Get user_id and user_secret for a user

            :param client_id : REQUIRED.  The application client identifier (eg: an Atlassian Confluence instance)

            :param client_secret : REQUIRED.  The application client secret (eg: an Atlassian Confluence instance)

            :param redirect_uri: REQUIRED.  x-www-form-urlencoded format

            :returns user_id : user_id for the user

            :returns user_secret : user_secret for the user
        """
        # Prepare request data variable
        request_data.update(request.httprequest.data)
        self._write_to_debug_log("application_user_client request_data", request_data)
        self._write_to_debug_log("application_user_client request_data length", len(request_data))

        # Check request data
        if len(request_data) == 0:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0001",
                'orestapi_message': _("No parameter found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Set user
        user_id = request.env.uid
        self._write_to_debug_log("application_user_client user", user_id)

        # Get client_id from request
        request_client_id = request_data.get('client_id')

        self._write_to_debug_log("application_user_client request_data", request_client_id)

        if not request_client_id:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0002",
                'orestapi_message': _("No client_id found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Get client_secret from request
        request_client_secret = request_data.get('client_secret')

        self._write_to_debug_log("application_user_client request_data", request_client_secret)

        if not request_client_secret:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0002",
                'orestapi_message': _("No client_secret found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Validate redirect_uri by unparsing it from x-www-form-urlencoded format
        if request_data.get('redirect_uri'):
            request_redirect_uri = urllib.parse.unquote(request_data.get('redirect_uri'))
            self._write_to_debug_log("application_user_client redirect_uri", request_redirect_uri)
        # If uri is not found, than return error
        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0003",
                'orestapi_message': _("Missing redirect URI")
            }
            return self._get_response_object(response_code, response_data)

        # Search for request redirect uri among the list of stored uris
        application_uri_object = request.env['oregional.restapi.application.uri'].sudo()
        existing_uri = application_uri_object.search([
            ('uri', '=', request_redirect_uri)
        ])
        self._write_to_debug_log("application_user_client existing_uri", existing_uri)

        if not existing_uri:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0004",
                'orestapi_message': _("Application redirect URI not found")
            }
            return self._get_response_object(response_code, response_data)

        # Get application
        application_object = request.env['oregional.restapi.application'].sudo()
        application = application_object.search([
            ('client_id', '=',request_client_id),
            ('client_secret', '=', request_client_secret),
            ('uri', '=', existing_uri.id)
        ])

        self._write_to_debug_log("application_user_client application", application)

        if not application:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0005",
                'orestapi_message': _("No application found")
            }
            return self._get_response_object(response_code, response_data)
        elif len(application) > 1:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiApplicationUserClient-0006",
                'orestapi_message': _("Oops, more than one application found")
            }
            return self._get_response_object(response_code, response_data)
        else:
            authorization_object = request.env['oregional.restapi.authorization'].sudo()
            authorization = authorization_object.search([
                ('application', '=', application),
                ('user', '=', user_id)
            ])

            self._write_to_debug_log("application_user_client authorization", authorization)

            if not authorization:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiApplicationUserClient-0007",
                    'orestapi_message': _("No authorization found")
                }
                return self._get_response_object(response_code, response_data)
            elif len(authorization) > 1:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiApplicationUserClient-0008",
                    'orestapi_message': _("Oops, more than one authorization found")
                }
                return self._get_response_object(response_code, response_data)
            else:
                response_code = 200
                response_data = {
                    'user_id': authorization.user_id,
                    'user_secret': authorization.user_secret,
                }
                return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/oauth2/authorization'], type="http", auth="user", csrf=False, website=True)
    def oregional_restapi_oauth2_authorization(self, **request_data):
        """ Oauth2 authorization

            Documentation: https://tools.ietf.org/html/rfc6749#section-4.1.1

            :param response_type : REQUIRED.  Value MUST be set to "code"

            :param client_id : REQUIRED.  The client identifier (eg: an Atlassian Confluence instance)

            :param redirect_uri: OPTIONAL.  x-www-form-urlencoded format

            :param scope: OPTIONAL. The scope of the access request NOT IMPLEMENTED

            :param state : RECOMMENDED. The value is included when redirecting the user-agent back to the client.

            :returns code : state https://tools.ietf.org/html/rfc6749#section-4.1.2

            :returns state : //tools.ietf.org/html/rfc6749#section-4.1.2
        """
        # Prepare request data variable
        request_data.update(request.httprequest.data)
        self._write_to_debug_log("oauth2_authorization request_data", request_data)
        self._write_to_debug_log("oauth2_authorization request_data length", len(request_data))

        # Check request data
        if len(request_data) == 0:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2Authorization-0001",
                'orestapi_message': _("No parameter found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Get client_id from request
        if request_data.get('client_id'):
            request_client_id = request_data.get('client_id')
        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2Authorization-0002",
                'orestapi_message': _("No client_id found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Get redirect_uri by unparsing it from x-www-form-urlencoded format
        if request_data.get('redirect_uri'):
            request_redirect_uri = urllib.parse.unquote(request_data.get('redirect_uri'))
            self._write_to_debug_log("oauth2_authorize redirect_uri", request_redirect_uri)
        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2Authorization-0003",
                'orestapi_message': _("No redirect_uri found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Search for request redirect uri among the list of stored uris
        application_uri_object = request.env['oregional.restapi.application.uri'].sudo()
        existing_uri = application_uri_object.search([
            ('uri', '=', request_redirect_uri)
        ])
        self._write_to_debug_log("oauth2_authorize existing_uri", existing_uri)

        # Check existing uri
        if existing_uri and len(existing_uri) == 1:
            # Check if application is active by making a search (it returns only active applications)
            application_object = request.env['oregional.restapi.application'].sudo()
            application = application_object.search([
                ('id', '=', existing_uri.application.id),
                ('client_id', '=', request_client_id),
                ('uri', '=', existing_uri.id)
            ])
            self._write_to_debug_log("oauth2_authorize application", application)

            if not application or len(application) > 1:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2Authorization-0004",
                    'orestapi_message': _("Could not find active application")
                }
                return self._get_response_object(response_code, response_data)

        # If no or too many existing url found, than return error
        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2Authorization-0005",
                'orestapi_message': _("Redirect URI not found or misconfigured")
            }
            return self._get_response_object(response_code, response_data)

        # Set user
        user_id = request.env.uid
        # Get user as object
        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        self._write_to_debug_log("oauth2_authorize user", user_id)

        # Now lets start checking if user already authorized this application and the URI
        user_authorization_object = request.env['oregional.restapi.authorization'].sudo()

        # # If the URI needs to be authorized individually
        if existing_uri.authorize_individually:
            user_authorization = user_authorization_object.search([
                ('user', '=', user.id),
                ('application', '=', application.id),
                ('authorization_uri', 'in', existing_uri.id)
            ])
            authorization_uri = request_redirect_uri

        # # Check only for the application if the URI does not need individual authorization
        else:
            user_authorization = user_authorization_object.search([
                ('user', '=', user.id),
                ('application', '=', application.id)
            ])
            authorization_uri = False

        # Get new code for existing authorization
        if user_authorization and len(user_authorization) == 1:
            authorization_code_object = request.env['oregional.restapi.authorization.code'].sudo()
            authorization_code = authorization_code_object.get_authorization_code(user_authorization)
            self._write_to_debug_log("oauth2_authorization NEW authorization_code for EXISTING", authorization_code)

        # Else create new authorization and get code
        else:
            new_authorization_object = request.env['oregional.restapi.authorization'].sudo()
            new_authorization = new_authorization_object.get_user_authorization(application, user, authorization_uri)
            self._write_to_debug_log("oauth2_authorization NEW authorization", new_authorization)

            new_authorization_code_object = request.env['oregional.restapi.authorization.code'].sudo()
            authorization_code = new_authorization_code_object.get_authorization_code(new_authorization)
            self._write_to_debug_log("oauth2_authorization NEW authorization_code for NEW", authorization_code)

        if authorization_code:
            response_code = authorization_code.code
            self._write_to_debug_log("oauth2_authorization response_code", response_code)
        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2Authorization-0006",
                'orestapi_message': _("Could not get authorization code")
            }
            return self._get_response_object(response_code, response_data)

        # Set state (the exact same value that was received in the request must be returned in the response)
        response_state = request_data.get('state')
        self._write_to_debug_log("oauth2_authorization response_state", response_state)

        # Redirect when necessary
        if request_redirect_uri:
            # Set target uri encoded params
            target_uri_encoded_params = werkzeug.url_encode({
                'code': response_code,
                'state': response_state
            })
            target_uri = request_redirect_uri + "?" + target_uri_encoded_params
            self._write_to_debug_log("oauth2_authorization target_uri", target_uri)

            # Return
            return werkzeug.utils.redirect(target_uri)

        # Else return json
        else:
            response_code = 200
            response_data = {
                'code': response_code,
                'state': response_state
            }
            return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/oauth2/access_token'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_oauth2_access_token(self, **request_data):
        """ Access Token Request using authorization_code or refresh_token

        Request: https://tools.ietf.org/html/rfc6749#section-4.1.3
        Response: https://tools.ietf.org/html/rfc6749#section-4.1.4

        :param grant_type: REQUIRED. Can be set to "authorization_code" or "refresh_token"

        :param code: The authorization code received from the authorization server.
                     REQUIRED if grant_type is "authorization_code".

        :param redirect_uri: REQUIRED, if the "redirect_uri" parameter was included in the
                             authorization request as described in Section 4.1.1, and their
                             values MUST be identical.

        :param refresh_token: REQUIRED if grant_type is "refresh_token"

        :param client_id: The client id for the application
                          REQUIRED if grant_type is "authorization_code"

        :param client_secret: The secret for the client_id
                              REQUIRED if grant_type is "authorization_code"

        :returns access_token

        :returns token_type

        :returns expires_in

        :returns refresh_token

        """
        # Prepare request data variable
        request_data.update(request.httprequest.data)
        self._write_to_debug_log("oauth2_authorization request_data", request_data)
        self._write_to_debug_log("oauth2_authorization request_data length", len(request_data))

        # Check request data
        if len(request_data) == 0:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2AccessToken-0001",
                'orestapi_message': _("No parameter found in request")
            }
            return self._get_response_object(response_code, response_data)

        # Get grant_type from request
        request_grant_type = request_data.get('grant_type')

        self._write_to_debug_log("oauth2_access_token grant_type", request_grant_type)

        if not request_grant_type:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2AccessToken-0020",
                'orestapi_message': _("No grant_type found in request")
            }
            return self._get_response_object(response_code, response_data)

        if request_grant_type == 'authorization_code':
            # Get code from request
            request_code = request_data.get('code')

            self._write_to_debug_log("oauth2_access_token request_code", request_code)

            if not request_code:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0030",
                    'orestapi_message': _("No code found in request")
                }
                return self._get_response_object(response_code, response_data)

            # Get client_id
            request_client_id = request_data.get('client_id')

            self._write_to_debug_log("oauth2_access_token request_client_id", request_client_id)

            if not request_client_id:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0040",
                    'orestapi_message': _("No client_id found in request")
                }
                return self._get_response_object(response_code, response_data)

            # Get client_secret
            request_client_secret = request_data.get('client_secret')

            self._write_to_debug_log("oauth2_access_token request_client_secret", request_client_secret)

            if not request_client_secret:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0050",
                    'orestapi_message': _("No client_secret found in request")
                }
                return self._get_response_object(response_code, response_data)

            # Get redirect_uri by unparsing it from x-www-form-urlencoded format
            request_redirect_uri = urllib.parse.unquote(request_data.get('redirect_uri'))

            self._write_to_debug_log("oauth2_access_token request_redirect_uri", request_redirect_uri)

            if not request_redirect_uri:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0051",
                    'orestapi_message': _("No redirect_uri found in request")
                }
                return self._get_response_object(response_code, response_data)

            # Validate client_id and client_secret and redirect_uri
            application = request.env['oregional.restapi.application'].sudo(). \
                get_application_from_id_secret_uri(request_client_id, request_client_secret, request_redirect_uri)
            self._write_to_debug_log("OrestapiOauth2AccessToken APPLICATION SEARCH request_client_id", request_client_id)
            self._write_to_debug_log("OrestapiOauth2AccessToken APPLICATION SEARCH request_client_secret", request_client_secret)
            self._write_to_debug_log("OrestapiOauth2AccessToken APPLICATION SEARCH request_redirect_uri", request_redirect_uri)


            if not request_redirect_uri:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0060",
                    'orestapi_message': _("Invalid application")
                }
                return self._get_response_object(response_code, response_data)

            # Validate authorization code
            if request.env['oregional.restapi.authorization.code'].sudo().is_valid_application_authorization_code(
                    application, request_code):
                # Assemble response data
                response_data = request.env['oregional.restapi.authorization'].sudo(). \
                    get_access_token_response_data_from_authorization_code(request_code)
                self._write_to_debug_log("OrestapiOauth2AccessToken RESPONSE_DATA", response_data)

                # Use authorization code (client should use access or refresh token after the code is used)
                request.env['oregional.restapi.authorization.code'].sudo().search([
                    ('code', '=', request_code)
                ]).use_code()

                # Return
                return self._get_response_object(200, response_data)
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0070",
                    'orestapi_message': _("Invalid, expired or already used authorization code")
                }
                return self._get_response_object(response_code, response_data)
        elif request_grant_type == 'refresh_token':
            # Get header info
            authorization_header = request.httprequest.headers.get('Authorization')
            if 'Basic' in authorization_header:
                self._write_to_debug_log("OrestapiOauth2AccessToken BASIC FOUND", False)
                request_base64 = request.httprequest.headers.get('Authorization').split(' ')[1]
                self._write_to_debug_log("OrestapiOauth2AccessToken request_base64", request_base64)

            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0201",
                    'orestapi_message': _("Invalid authorization header")
                }
                return self._get_response_object(response_code, response_data)

            # Validate basic authentication from base64 application code
            if request_base64:
                # Get base64 from application
                application = request.env['oregional.restapi.application'].sudo().search([
                    ('client_http_basic_access_authentication', '=', request_base64)
                ])
                self._write_to_debug_log("OrestapiOauth2AccessToken application", application)
                self._write_to_debug_log("OrestapiOauth2AccessToken client_http_basic_access_authentication", application.client_http_basic_access_authentication)

                if application and len(application) == 1:
                    # Get refresh token
                    refresh_token = request_data.get('refresh_token')

                    if refresh_token:
                        # Check if refresh token is valid
                        is_valid_refresh_token = request.env['oregional.restapi.authorization'].sudo(). \
                            is_valid_refresh_token(refresh_token)

                        if is_valid_refresh_token:
                            # Issue access token and new refresh token
                            response_data = request.env['oregional.restapi.authorization'].sudo(). \
                                get_access_token_response_data_from_refresh_token(refresh_token)
                            return self._get_response_object(200, response_data)
                        else:
                            response_code = 401
                            response_data = {
                                'orestapi_code': "OrestapiOauth2AccessToken-0205",
                                'orestapi_message': _("Invalid refresh token")
                            }
                            return self._get_response_object(response_code, response_data)
                    else:
                        response_code = 401
                        response_data = {
                            'orestapi_code': "OrestapiOauth2AccessToken-0203",
                            'orestapi_message': _("Refresh token not found in request")
                        }
                        return self._get_response_object(response_code, response_data)
                else:
                    response_code = 401
                    response_data = {
                        'orestapi_code': "OrestapiOauth2AccessToken-0204",
                        'orestapi_message': _("Client http basic access authentication failed")
                    }
                    return self._get_response_object(response_code, response_data)
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0202",
                    'orestapi_message': _("No http basic access authentication found in authorization header")
                }
                return self._get_response_object(response_code, response_data)
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiOauth2AccessToken-0220",
                    'orestapi_message': _("Basic http access authorization not found in header")
                }
                return self._get_response_object(response_code, response_data)

        else:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiOauth2AccessToken-0021",
                'orestapi_message': _("Invalid grant_type")
            }
            return self._get_response_object(response_code, response_data)

    @http.route(['/orestapi/application/confluence/link'], type="http", auth="user", csrf=False, website=True)
    def oregional_restapi_application_confluence_link(self, **request_data):
        """ Create application link between an Atlassian Confluence application and Odoo

            :param client_id : REQUIRED.  The client identifier (eg: an Atlassian Confluence instance)

            :param client_secret : REQUIRED.  The client secret (eg: an Atlassian Confluence instance)

            :param redirect_uri: OPTIONAL.  x-www-form-urlencoded format

            :param state : RECOMMENDED. The value is included when redirecting the user-agent back to the client.


            :returns odoo_id :
            :returns odoo_secret :
        """
        # Prepare request data variable
        pass

    @http.route(['/orestapi/record/name_search'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_record_name_search(self, **request_data):
        """Get a dictionary of records for a model by performing a name_search operation

        Request parameters:
            - model: REQUIRED, string, the name of the model to be searched
            - name: OPTIONAL, string, the fragment of display_name to be searched
            - limit: OPTIONAL, integer, number of search results to be returned
            - offset: OPTIONAL, integer, for search result offsets
            - order: OPTIONAL, string, the field names to be used for ordering as per Odoo domain conventions

        :param request_data: data contained in the https request

        :returns list of dictionaries with record data
        """
        # Get authorization from request_data
        authorization = request.env['oregional.restapi.authorization'].sudo()\
            .get_valid_authorization_from_request(request)

        if not authorization:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiNameSearch-0010",
                'orestapi_message': _("Not authorized")
            }
            return self._get_response_object(response_code, response_data)
        else:
            # Update request_data
            request_data.update(request.httprequest.data or {})
            self._write_to_debug_log("record name_search request data", request_data)

            # Get info from request_data
            model_name = request_data.get('model')
            self._write_to_debug_log("record name_search request_model", model_name)

            if not model_name:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiNameSearch-0020",
                    'orestapi_message': _("Model not provided")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.can_user_read_model(authorization.user, model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiNameSearch-0021",
                    'orestapi_message': _("User does not have read permission to the model")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.is_allowed_model(model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiNameSearch-0022",
                    'orestapi_message': _("Model not allowed")
                }
                return self._get_response_object(response_code, response_data)
            else:
                pass

            # Get offset
            if request_data.get('offset'):
                offset = int(request_data['offset'])
                if not offset:
                    response_code = 401
                    response_data = {
                        'orestapi_code': "OrestapiApplicationGetModel-0050",
                        'orestapi_message': _("Offset must be integer")
                    }
                    return self._get_response_object(response_code, response_data)
            else:
                offset = 0

            # Get limit
            if request_data.get('limit'):
                limit = int(request_data['limit'])
                if not limit:
                    response_code = 401
                    response_data = {
                        'orestapi_code': "OrestapiApplicationGetModel-0060",
                        'orestapi_message': _("Limit must be integer")
                    }
                    return self._get_response_object(response_code, response_data)
            else:
                limit = 20

            # Get order
            if request_data.get('order'):
                order = request_data['order']
            else:
                order = 'display_name'

            # Do name search
            model_object = request.env[model_name].sudo()
            self._write_to_debug_log("record name_search param model_name", model_name)
            self._write_to_debug_log("record name_search param offset", offset)
            self._write_to_debug_log("record name_search param limit", limit)
            self._write_to_debug_log("record name_search param order", order)

            # If name is provided, than perform a name_search
            if request_data.get('name'):
                # Prepare name
                name = request_data['name']
                self._write_to_debug_log("record name_search name", name)

                # Try to do a name_search
                try:
                    name_search_recordset = model_object.name_search(name, False, 'ilike', False)

                    # Unfortunately name_search does not have offset parameter, so we need to search again
                    search_ids = []

                    for name_search_record in name_search_recordset:
                        search_ids.append(name_search_record[0])

                    # Do new search now with offset, order and limit
                    search_recordset = model_object.search([
                        ('id', 'in', search_ids)
                    ])

                # If runs to error, do a normal search
                except (RuntimeError, TypeError, NameError):
                    # Do search
                    search_recordset = model_object.search([
                        ('display_name', 'ilike', name)
                    ], offset=offset, limit=limit, order=order)

            # Else just make a search without domain
            else:
                search_recordset = model_object.search([], offset=offset, limit=limit, order=order)

            search_recordset_count = len(search_recordset)

            # Prepare result list
            search_result = []

            # Get action TODO not working for crm lead for example
            action_object = request.env['ir.actions.act_window'].sudo()
            actions = action_object.search([
                ('res_model', '=', model_name),
                ('type', '=', "ir.actions.act_window")
            ])

            if actions:
                for action in actions:
                    # Get menu
                    menu_object = request.env['ir.ui.menu'].sudo()
                    menu_action_search = 'ir.actions.act_window,' + str(action.id)

                    self._write_to_debug_log("menu_action_search", menu_action_search)

                    menu = menu_object.search([('action', '=', menu_action_search)], limit=1)

                    if menu:
                        action_id = action.id
                        menu_id = menu.id
                        break
                    else:
                        action_id = False
                        menu_id = False
            else:
                action_id = False
                menu_id = False

            # Prepare result header_data
            search_result_header_data = {
                'model': model_name,
                'action_id': action_id,
                'menu_id': menu_id,
                'count': search_recordset_count,
                'offset': offset,
                'limit': limit
            }

            # Prepares search result header
            search_result_header = {
                'header': search_result_header_data
            }

            # Append header to result
            search_result.append(search_result_header)

            # Prepare result data
            search_result_item_data = []

            # Iterate through search result
            if len(search_recordset) > 0:
                for search_record in search_recordset:
                    search_record_data = {
                        'id': search_record.id,
                        'display_name': search_record.name_get()[0][1]
                    }

                    # Append to result_data list
                    search_result_item_data.append(search_record_data)

            # Append item result data list to result
            search_result_data = {
                'data': search_result_item_data
            }

            # Append result data to result
            search_result.append(search_result_data)

            # Final result
            response_code = 200
            response_data = search_result
            result = self._get_response_object(response_code, response_data)
            self._write_to_debug_log("record name_search result", result)

            # Return
            return result

    @http.route(['/orestapi/record/read'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_record_read(self, **request_data):
        """ Get field values of one or more records using read operation

        Expected parameters in the request:
            - model (string): the related model
            - ids (list): list of record ids, use one item in the list if you need only one record
            - fields (list): list of field names

        :param request_data: data contained in the https request

        :returns list of dictionaries with record field values
        """
        # Get authorization from request_data
        authorization = request.env['oregional.restapi.authorization'].sudo()\
            .get_valid_authorization_from_request(request)

        if not authorization:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiContentRecordRead-0010",
                'orestapi_message': _("Not authorized")
            }
            return self._get_response_object(response_code, response_data)
        else:
            # Update request_data
            request_data.update(request.httprequest.data or {})
            self._write_to_debug_log("record name_search record read", request_data)

            # Get info from request_data
            model_name = request_data.get('model')
            self._write_to_debug_log("record name_search record read", model_name)

            if not model_name:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiContentRecordRead-0020",
                    'orestapi_message': _("Model not provided")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.can_user_read_model(authorization.user, model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiContentRecordRead-0021",
                    'orestapi_message': _("User does not have read permission to the model")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.is_allowed_model(model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiContentRecordRead-0030",
                    'orestapi_message': _("Model not allowed")
                }
                return self._get_response_object(response_code, response_data)
            else:
                pass

            # Get record ids
            if request_data.get('ids'):
                record_ids = json.loads(request_data['ids'])
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiContentRecordRead-0040",
                    'orestapi_message': _("Ids not provided")
                }
                return self._get_response_object(response_code, response_data)

            # Get fields
            if request_data.get('fields'):
                field_list = json.loads(request_data['fields'])
            else:
                field_list = False

            # Initialize model object
            model_object = request.env[model_name].sudo()
            self._write_to_debug_log("record name_search search param model", model_name)
            self._write_to_debug_log("record name_search search param record_ids", record_ids)
            self._write_to_debug_log("record name_search search param field_list", field_list)

            # Perform a search for the id as the user
            records = model_object.sudo(authorization.user.id).search([('id', 'in', record_ids)])

            # Prepare result list
            result = []

            # Get action TODO not working for crm lead for example
            action_object = request.env['ir.actions.act_window'].sudo()
            actions = action_object.search([
                ('res_model', '=', model_name),
                ('type', '=', "ir.actions.act_window")
            ])

            if actions:
                for action in actions:
                    # Get menu
                    menu_object = request.env['ir.ui.menu'].sudo()
                    menu_action_search = 'ir.actions.act_window,' + str(action.id)
                    self._write_to_debug_log("record name_search menu_action_search", menu_action_search)

                    menu = menu_object.search([('action', '=', menu_action_search)], limit=1)

                    if menu:
                        action_id = action.id
                        menu_id = menu.id
                        break
                    else:
                        action_id = False
                        menu_id = False
            else:
                action_id = False
                menu_id = False

            # Prepare result header_data
            result_header_data = {
                'model': model_name,
                'action_id': action_id,
                'menu_id': menu_id,
            }

            # Prepares result header
            result_header = {
                'header': result_header_data
            }

            # Append header to result
            result.append(result_header)

            # Prepare result data list
            result_data_list = []

            # If record is found, than perform a read operation to get the fields
            if records:
                for record in records:
                    read_result = record.read(field_list)
                    result_data_list += read_result

                # Prepare result data
                result_data = {
                    'data': result_data_list
                }

                # Append data to result
                result.append(result_data)

            # Else return error
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiContentRecordRead 0050",
                    'orestapi_message': _("Record not found")
                }
                return self._get_response_object(response_code, response_data)

            # Final result
            response_code = 200
            response_data = result
            result = self._get_response_object(response_code, response_data)
            self._write_to_debug_log("record name_search result", result)

            # Return
            return result

    @http.route(['/orestapi/model/field'], type="http", auth="public", csrf=False, website=True)
    def oregional_restapi_model_field(self, **request_data):
        """ Get data about one or many available fields of a model

        Expected parameters in the request:
            - model (string): the related model
            - names (list): list of field names (the name field in the model called ir.model.fields)
            - data (list): list of field names to return for the queried field names (confusing but accurate, read it again!)

        :param request_data: data contained in the https request

        :returns dictionaries with model fields
        """
        # Get authorization from request_data
        authorization = request.env['oregional.restapi.authorization'].sudo()\
            .get_valid_authorization_from_request(request)

        if not authorization:
            response_code = 401
            response_data = {
                'orestapi_code': "OrestapiModelFields-0010",
                'orestapi_message': _("Not authorized")
            }
            return self._get_response_object(response_code, response_data)
        else:
            # Update request_data
            request_data.update(request.httprequest.data or {})
            self._write_to_debug_log("model fields request_data", request_data)

            # Get info from request_data
            model_name = request_data.get('model')
            self._write_to_debug_log("model field get request model", model_name)

            if not model_name:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiModelField-0020",
                    'orestapi_message': _("Model not provided")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.can_user_read_model(authorization.user, model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiModelField-0021",
                    'orestapi_message': _("User does not have read permission to the model")
                }
                return self._get_response_object(response_code, response_data)
            elif not authorization.application.model_scheme.is_allowed_model(model_name):
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiModelField-0022",
                    'orestapi_message': _("Model is not allowed")
                }
                return self._get_response_object(response_code, response_data)
            else:
                pass

            # Get list of field names for which data is requested
            if request_data.get('names'):
                try:
                    request_field_name_list = json.loads(request_data['names'])

                    if not isinstance(request_field_name_list, list):
                        response_code = 401
                        response_data = {
                            'orestapi_code': "OrestapiModelField-0032",
                            'orestapi_message': _("Names parameter must be a list!")
                        }
                        return self._get_response_object(response_code, response_data)
                except:
                    response_code = 401
                    response_data = {
                        'orestapi_code': "OrestapiModelField-0031",
                        'orestapi_message': _("Could not read load names parameter, maybe not a list?")
                    }
                    return self._get_response_object(response_code, response_data)
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiModelField-0030",
                    'orestapi_message': _("Names parameter is mandatory!")
                }
                return self._get_response_object(response_code, response_data)

            # Get requested data
            if request_data.get('data'):
                try:
                    request_field_data_list = json.loads(request_data['data'])

                    if not isinstance(request_field_data_list, list):
                        response_code = 401
                        response_data = {
                            'orestapi_code': "OrestapiModelField-0041",
                            'orestapi_message': _("Data parameter must be a list!")
                        }
                        return self._get_response_object(response_code, response_data)
                except:
                    response_code = 401
                    response_data = {
                        'orestapi_code': "OrestapiModelField-0040",
                        'orestapi_message': _("Could not read load data parameter, maybe not a list?")
                    }
                    return self._get_response_object(response_code, response_data)
            else:
                request_field_data_list = False

            # Get allowed fields for the model scheme
            result_fields = authorization.application.model_scheme.get_allowed_fields(model_name, request_field_name_list)
            self._write_to_debug_log("model field get_result_fields model", model_name)
            self._write_to_debug_log("model field get_result_fields request_field_name_list", request_field_name_list)
            self._write_to_debug_log("model field get_result_fields result_fields", result_fields)

            # If record is found, than perform a read operation to get the fields
            if result_fields:
                result = []
                for field in result_fields:
                    # Unknown field_data_list values will be ignored by the read() operation
                    read_result = field.read(request_field_data_list)
                    result += read_result

            # Else return error
            else:
                response_code = 401
                response_data = {
                    'orestapi_code': "OrestapiModelField-0040",
                    'orestapi_message': _("Field not found")
                }
                return self._get_response_object(response_code, response_data)

            # Final result
            response_code = 200
            response_data = result
            result = self._get_response_object(response_code, response_data)
            self._write_to_debug_log("model fields search params result", result)

            # Return
            return result

    def _get_response_object(self, status_code, data=None):
        """ Returns Response Object with given status code and status

            https://httpwg.org/specs/rfc7230.html

            :param status_code: 3 digit integer https://httpwg.org/specs/rfc7231.html#status.codes

            :param body: data to be included in the response body parsed as json

            :returns: response object
        """
        # Create response object
        response = Response()

        # Set status code
        response.status_code = status_code
        self._write_to_debug_log("_get_response_object response.status_code", response.status_code)

        response.status = str(status_code)

        self._write_to_debug_log("_get_response_object response.status", response.status)

        # Set body
        if data:
            try:
                response.data = isinstance(data, str) and data or json.dumps(data)
            except ValueError:
                response.data = str(data)

        self._write_to_debug_log("_get_response_object response.data", response.data)

        # Return
        return response

    # Debugger
    def _write_to_debug_log(self, title, data=False):
        if request.env['ir.config_parameter'].sudo().get_param('oregional_restapi.oregional_rest_api_is_debug_mode'):
            debug_title = "--XXXX-- " + title + " --XXXX--"
            _logger.debug(debug_title)
            if data:
                _logger.debug(data)
        else:
            pass
