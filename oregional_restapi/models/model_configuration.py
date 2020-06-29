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
class OregionalRestapiModelConfiguration(models.Model):
    # Private attributes
    _name = 'oregional.restapi.model.configuration'
    _description = "REST API model configuration"
    _inherit = ['mail.thread']

    # Default methods

    # Fields declaration
    active = fields.Boolean(
        default=True,
        string="Active",
        track_visibility='onchange',
    )
    company = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id.id,
        index=True,
        string="Company",
    )
    description = fields.Text(
        copy=False,
        help="Additional information",
        string="Description",
        translate=True,
        track_visibility='onchange',
    )
    field = fields.Many2many(
        comodel_name='ir.model.fields',
        column1='model_scheme',
        column2='field',
        copy=True,
        help="Available fields for the model scheme",
        index=True,
        relation='oregional_restapi_model_scheme_field_rel',
        string="Field",
    )
    field_limit = fields.Selection(
        default='none',
        help="None means no limits, blacklist denies, whitelist allows only the selected fields",
        selection=[
            ('none', "None"),
            ('blacklist', "Blacklist"),
            ('whitelist', "Whitelist")
        ],
        track_visibility='onchange',
        string="Field Limit",
    )
    filter = fields.Many2one(
        comodel_name='ir.filters',
        copy=True,
        index=True,
        string="Filter",
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
    is_base = fields.Boolean(
        copy=False,
        default=False,
        string="Base",
    )
    model = fields.Many2one(
        comodel_name='ir.model',
        copy=True,
        index=True,
        required=True,
        string="Model",
        track_visibility='onchange',
    )
    model_display_name = fields.Char(
        copy=True,
        index=True,
        string="Model Display Name",
        translate=True,
        track_visibility='onchange',
    )
    model_name = fields.Char(
        index=True,
        related='model.model',
        store=True,
        string="Model Technical Name",
    )
    name = fields.Char(  # Name of the other application eg: Atlassian Jira
        required=True,
        string="Configuration Name",
        track_visibility='onchange',
        translate=True,
    )
    scheme = fields.Many2many(
        comodel_name='oregional.restapi.model.scheme',
        column1='configuration',
        column2='scheme',
        copy=True,
        index=True,
        relation='oregional_restapi_model_configuration_rel',
        string="Scheme",
        track_visibility='onchange',
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges
    # # Onchange field
    @api.onchange('field_limit')
    def onchange_field_limit(self):
        if self.field_limit == 'none':
            self.field = False
        else:
            pass

    # # Onchange model
    @api.onchange('model')
    def onchange_model(self):
        if self.model:
            if not self.model_display_name:
                self.model_display_name = self.model.name

            return {'domain': {
                'field': [('model_id', '=', self.model.id)],
                'filter': [('model_id', '=', self.model.name)]
            }}

    # CRUD methods (and name_get, name_search, ...) overrides
    # # Override create
    @api.model
    def create(self, values):
        # Resize images
        tools.image_resize_images(values)

        # Check if name already exists
        if values.get('name'):
            existing = self.env['oregional.restapi.model.configuration'].search([
                ('name', '=', values['name'])
            ], limit=1)
            if existing:
                values.update({
                    'name': existing.name + " -" + _("copy")
                })

        # Execute create
        return super(OregionalRestapiModelConfiguration, self).create(values)

    # # Override write
    @api.multi
    def write(self, values):
        for item in self:
            # Resize images
            tools.image_resize_images(values)

            # Check if name already exists
            if values.get('name'):
                existing = self.env['oregional.restapi.model.configuration'].search([
                    ('name', '=', values['name'])
                ], limit=1)
                if existing:
                    values.update({
                        'name': existing.name + " -" + _("copy")
                    })

        # Execute create
        return super(OregionalRestapiModelConfiguration, self).write(values)

    # Action methods

    # Business methods
    @api.multi
    def get_allowed_fields(self, field_name_list=False):
        """ Get allowed fields

        :param field_name_list : optional list of fields names to filter for, unrecognized field names are ignored

        :return List of field objects
        """
        self._write_to_debug_log("model_configuration get_allowed_fields called")

        # Ensure one
        self.ensure_one()

        # Process field_name_list, it should filter out any unknown fields
        if field_name_list:
            if not isinstance(field_name_list, list):
                self._write_to_debug_log("model_configuration get_allowed_fields isinstance list", False)
                return False
            else:
                filtered_fields = self.env['ir.model.fields'].search([
                    ('model_id', '=', self.model.id),
                    ('name', 'in', field_name_list)
                ])
        else:
            filtered_fields = self.env['ir.model.fields'].search([
                    ('model_id', '=', self.model.id)
                ])
        self._write_to_debug_log("model_configuration get_allowed_fields filtered_fields", filtered_fields)

        # Initialize result
        result = []

        # Process if limit is none
        if self.field_limit == 'none':
            self._write_to_debug_log("model_configuration get_allowed_fields field_limit=none", False)
            result = self.env['ir.model.fields'].search([
                ('id', 'in', filtered_fields.ids),
            ])
        # Process if limit is blacklist
        elif self.field_limit == 'blacklist':
            self._write_to_debug_log("model_configuration get_allowed_fields field_limit=blacklist", False)
            # Get blacklisted fields
            blacklisted_fields = self.field

            # Compute result
            result = [x for x in filtered_fields if x not in blacklisted_fields]
        # Process if limit is whitelist
        elif self.field_limit == 'whitelist':
            self._write_to_debug_log("model_configuration get_allowed_fields field_limit=whitelist", False)
            result = [y for y in filtered_fields if y in self.field]
        else:
            pass

        # Return
        self._write_to_debug_log("model_configuration get_allowed_fields result", result)
        return result

        # Business methods

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