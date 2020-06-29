# -*- coding: utf-8 -*-
# 1 : imports of python lib
import base64
import logging

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models, tools  # alphabetically ordered

# 3 : imports from odoo modules

# 4: variable declarations
_logger = logging.getLogger(__name__)


# Class
class OregionalRestapiApplication(models.Model):
    # Private attributes
    _name = 'oregional.restapi.application'
    _description = "REST API application"
    _inherit = ['mail.thread']
    _order = 'name'

    # Default methods

    # Fields declaration
    access_token_expiry = fields.Integer(
        default=3600,
        help="Access token expiry in seconds",
        string="Access Token Expiry",
        track_visibility='onchange',
    )
    active = fields.Boolean(
        default=True,
        string="Active",
        track_visibility='onchange',
    )
    authorization_code_expiry = fields.Integer(
        default=600,
        help="Authorization code expiry in seconds",
        string="Authorization Code Expiry",
        track_visibility='onchange',
    )
    authorization_code_retain = fields.Integer(
        default=0,
        help="Number of days to keep used authorization codes",
        string="Authorization Code Retain",
        track_visibility='onchange',
    )
    client_access_token_expiry_limit = fields.Integer(
        help="Client access token expiry limit in seconds",
        string="Client Access Token Expiry Limit",
        track_visibility='onchange',
    )
    client_http_basic_access_authentication = fields.Char(
        compute='_compute_client_http_basic_access_authentication',
        help="Client http basic access authentication encoded in base64",
        store=True,
        string="Client Http Basic Access Authentication",
    )
    client_id = fields.Char(
        help="Identifier of the client application",
        string="Client ID",
        track_visibility='onchange',
    )
    client_secret = fields.Char(
        help="Secret of the client application",
        string="Client Secret",
    )
    company = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id.id,
        index=True,
        string="Company",
    )
    description = fields.Text(
        help="Additional information",
        string="Description",
        translate=True,
        track_visibility='onchange',
    )
    image = fields.Binary(
        string="Image",
    )
    image_small = fields.Binary(
        string="Small-sized image",
    )
    image_medium = fields.Binary(
        string="Medium-sized image",
    )
    model_scheme = fields.Many2one(
        comodel_name='oregional.restapi.model.scheme',
        copy=True,
        help="Linked model scheme",
        index=True,
        required=True,
        string="Model Scheme",
    )
    name = fields.Char(  # Name of the other application eg: Atlassian Jira
        required=True,
        string="Name",
        track_visibility='onchange',
        translate=True,
    )
    odoo_id = fields.Char(
        help="Identifier of this Odoo instance used by the client application",
        string="Own ID",
        track_visibility='onchange',
    )
    odoo_secret = fields.Char(
        help="Secret for this Odoo instance used by the client application",
        string="Own Secret",
    )
    refresh_token_expiry = fields.Integer(
        default=0,
        help="Refresh token expiry in seconds (use 0 for no expiry)",
        string="Refresh Token Expiry",
    )
    uri = fields.One2many(
        comodel_name='oregional.restapi.application.uri',
        help="URIs for the application",
        inverse_name='application',
        name="URI",
    )

    # Compute and search fields, in the same order of fields declaration
    @api.depends('client_id','client_secret')
    @api.multi
    def _compute_client_http_basic_access_authentication(self):
        for item in self:
            if item.client_id and item.client_secret:
                client_data = item.client_id + ":" + item.client_secret
                client_data_bytes = client_data.encode("utf-8")
                item.client_http_basic_access_authentication = base64.b64encode(client_data_bytes)
                self._write_to_debug_log("application _compute_client_http_basic_access_authentication", item.client_http_basic_access_authentication)

    # Constraints and onchanges
    # # Onchange model_limit
    @api.onchange('model_limit')
    def onchange_model_limit(self):
        if self.model_limit == 'none':
            self.model = False
        else:
            pass

    # CRUD methods (and name_get, name_search, ...) overrides
    # # Override create
    @api.model
    def create(self, values):
        # Resize images
        tools.image_resize_images(values)

        # Check if name already exists
        if values.get('name'):
            existing = self.env['oregional.restapi.application'].search([
                ('name', '=', values['name'])
            ], limit=1)
            if existing:
                values.update({
                    'name': existing.name + " -" + _("copy")
                })

        # Execute create
        return super(OregionalRestapiApplication, self).create(values)

    # # Override write
    @api.multi
    def write(self, values):
        for item in self:
            # Resize images
            tools.image_resize_images(values)

            # Check if name already exists
            if values.get('name'):
                existing = self.env['oregional.restapi.application'].search([
                    ('name', '=', values['name'])
                ], limit=1)
                if existing:
                    values.update({
                        'name': existing.name + " -" + _("copy")
                    })

        # Execute create
        return super(OregionalRestapiApplication, self).write(values)

    # Action methods
    # # Generate client_id
    @api.multi
    def action_generate_client_id(self):
        # Ensure one
        self.ensure_one()

        # Generate
        client_id = self.generate_client_id()

        # Write
        self.write({
            'client_id': client_id
        })

        # Return
        return

    # # Generate client_secret
    @api.multi
    def action_generate_client_secret(self):
        # Ensure one
        self.ensure_one()

        # Generate
        client_secret = self.generate_client_secret()

        # Write
        self.write({
            'client_secret': client_secret
        })

        # Return
        return

    # # Generate odoo id
    @api.multi
    def action_generate_odoo_id(self):
        # Ensure one
        self.ensure_one()

        # Generate
        odoo_id = self.generate_odoo_id()

        # Write
        self.write({
            'odoo_id': odoo_id
        })

        # Return
        return

    # # Generate odoo secret
    @api.multi
    def action_generate_odoo_secret(self):
        # Ensure one
        self.ensure_one()

        # Generate
        odoo_secret = self.generate_odoo_secret()

        # Write
        self.write({
            'odoo_secret': odoo_secret
        })

        # Return
        return

    # Business methods
    # # Generate client_id
    @api.multi
    def generate_client_id(self):
        # Ensure one
        self.ensure_one()

        # Return
        return self._get_token()

    # # Generate client_secret
    @api.multi
    def generate_client_secret(self):
        # Ensure one
        self.ensure_one()

        # Return
        return self._get_token()

    # # Generate odoo id
    @api.multi
    def generate_odoo_id(self):
        # Ensure one
        self.ensure_one()

        # Return
        return self._get_token()

    # # Generate odoo secret
    @api.multi
    def generate_odoo_secret(self):
        # Ensure one
        self.ensure_one()

        # Return
        return self._get_token()

    # # Token generation
    @api.multi
    def _get_token(self):
        authorization_object = self.env['oregional.restapi.authorization']

        return authorization_object._get_token()

    @api.model
    def get_application_from_id_secret_uri(self, client_id, client_secret, uri):
        """ Get an application based on client_id, client_secret and uri"""
        application = self.env['oregional.restapi.application'].search([
            ('client_id', '=', client_id),
            ('client_secret', '=', client_secret)
        ])

        if application and len(application) == 1:
            redirect_uri = self.env['oregional.restapi.application.uri'].search([
                ('application', '=', application.id),
                ('uri', '=', uri)
            ])

            if redirect_uri:
                return application
            else:
                return False
        else:
            return False

    def do_client_basic_access_authentication(self, request):
        """ Perform basic access authentication for the client

        :param: request: http request

        :returns: Application object or False
        """
        # Search for authorization in the request header
        if request.httprequest.headers.get('Authorization'):
            authorization_header = request.httprequest.headers.get('Authorization')

            # If type Basic, than get the base64 encoded string
            if 'Basic' in authorization_header:
                request_base64 = request.httprequest.headers.get('Authorization').split(' ')[1]

                # Validate request_base64 against locally stored base64
                application = self.env['oregional.restapi.application'].search([
                    ('client_http_basic_access_authentication', '=', request_base64),
                    '|',
                    ('active', '=', True),
                    ('active', '=', False)
                ])
                if application and len(application) == 1:
                    return application
                else:
                    return False
            else:
                return False
        else:
            return False

    # # Debugger
    def _write_to_debug_log(self, title, data=False):
        if self.env['ir.config_parameter'].sudo().get_param(
                'oregional_restapi.oregional_rest_api_is_debug_mode'):
            debug_title = "--XXXX-- " + title + " --XXXX--"
            _logger.debug(debug_title)
            if data:
                _logger.debug(data)
        else:
            pass

