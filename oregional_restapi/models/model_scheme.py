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
class OregionalRestapiModelScheme(models.Model):
    # Private attributes
    _name = 'oregional.restapi.model.scheme'
    _description = "REST API model scheme"
    _inherit = ['mail.thread']
    _order = 'name'

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
    is_base = fields.Boolean(
        copy=False,
        default=False,
        string="Base",
    )
    model_blacklist = fields.Many2many(
        comodel_name='ir.model',
        column1='application',
        column2='model',
        copy=True,
        help="List of blacklisted models for the application",
        index=True,
        relation='oregional_restapi_application_model_blacklist_rel',
        string="Model Blacklist",
    )
    model_whitelist = fields.Many2many(
        comodel_name='oregional.restapi.model.configuration',
        column1='scheme',
        column2='configuration',
        copy=True,
        help="List of whitelisted model configurations for the application",
        index=True,
        relation='oregional_restapi_model_configuration_rel',
        string="Model Configuration Whitelist",
        track_visibility='onchange',
    )
    model_limit = fields.Selection(
        default='none',
        help="None means no limits, blacklist denies, whitelist allows only the selected models",
        selection=[
            ('none', "None"),
            ('blacklist', "Blacklist"),
            ('whitelist', "Whitelist")
        ],
        track_visibility='onchange',
        string="Model Limit",
    )
    name = fields.Char(  # Name of the other application eg: Atlassian Jira
        required=True,
        string="Name",
        track_visibility='onchange',
        translate=True,
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides
    # # Override create
    @api.model
    def create(self, values):
        # Resize images
        tools.image_resize_images(values)

        # Check if name already exists
        if values.get('name'):
            existing = self.env['oregional.restapi.model.scheme'].search([
                ('name', '=', values['name'])
            ], limit=1)
            if existing:
                values.update({
                    'name': existing.name + " -" + _("copy")
                })

        # Execute create
        return super(OregionalRestapiModelScheme, self).create(values)

    # # Override write
    @api.multi
    def write(self, values):
        for item in self:
            # Resize images
            tools.image_resize_images(values)

            # Check if name already exists
            if values.get('name'):
                existing = self.env['oregional.restapi.model.scheme'].search([
                    ('name', '=', values['name'])
                ], limit=1)
                if existing:
                    values.update({
                        'name': existing.name + " -" + _("copy")
                    })

        # Execute create
        return super(OregionalRestapiModelScheme, self).write(values)

    # Action methods
    # # List related applications
    @api.multi
    def action_list_application(self):
        # Ensure one
        self.ensure_one()

        # Linked applications
        return {
            'domain': [('model_scheme', '=', self.id)],
            'name': _("Application"),
            'res_model': 'oregional.restapi.application',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form'
        }

    # Business methods
    @api.model
    def can_user_read_model(self, user, model_name):
        """ Check if a user can read a models

        :param user: a res.users object

        :param model_name: technical name of the model, eg: project.task, crm.lead, res.partner, etc

        :return True or False
        """
        self._write_to_debug_log("model_scheme can_user_read_model called", False)
        self._write_to_debug_log("model_scheme can_user_read_model user", user)
        self._write_to_debug_log("model_scheme can_user_read_model model_name", model_name)
        # Initialize
        result = False

        # Try
        try:
            search_result = self.env[model_name].sudo(user.id).search([], limit=1)
            self._write_to_debug_log("model_scheme can_user_read_model search_result", search_result)
            result = True
        except:
            pass

        # Return
        if result:
            self._write_to_debug_log("model_scheme can_user_read_model result", "TRUE")
        else:
            self._write_to_debug_log("model_scheme can_user_read_model result", "FALSE")
        return result

    @api.model
    def is_allowed_model(self, model_name):
        """ Check if a model is allowed for the scheme

        :param model_name: technical name of the model, eg: project.task, crm.lead, res.partner, etc

s        :return True or False
        """
        # Initialize
        result = False

        # Get model as object
        model = self.env['ir.model'].search([('model', '=', model_name)])

        # Get allowed models
        allowed_models = self.get_allowed_models()

        # Check
        for item in allowed_models:
            if model == item[0]:
                result = True

        # Return
        return result

    @api.multi
    def get_allowed_models(self):
        """ Get allowed models for a scheme

        :return List of model information (model, model_display_name)
        """
        # Ensure one
        self.ensure_one()

        # Initialize list
        result = []

        # Process if limit is none
        if self.model_limit == 'none':
            self._write_to_debug_log("model_scheme get_allowed_models model_limit=none", False)
            models = self.env['ir.model'].search([])
            for model in models:
                # Assemble result
                result.append([model, model.name])
        # Process if limit is blacklist
        elif self.model_limit == 'blacklist':
            self._write_to_debug_log("model_scheme get_allowed_models model_limit=blacklist", False)
            # Get all models
            all_models = self.env['ir.model'].search([])

            # Get blacklisted models
            blacklisted_models = self.model_blacklist

            # Compute allowed models
            allowed_models = all_models - blacklisted_models

            # Assemble result
            for model in allowed_models:
                # Assemble result
                result.append([model, model.name])
        # Process if limit is whitelist
        elif self.model_limit == 'whitelist':
            self._write_to_debug_log("model_scheme get_allowed_models model_limit=whitelist", False)
            # Get whitelisted configurations models
            for configuration in self.model_whitelist:
                # Assemble result
                result.append([configuration.model, configuration.model_display_name or configuration.model.name])
        else:
            pass

        # Return
        return result

    @api.multi
    def get_allowed_fields(self, model_name, request_field_list=False):
        """ Get allowed fields for a model in a scheme

        :param model_name: the technical name of the model (eg: res.partner)

        :return List of field ids
        """
        self._write_to_debug_log("model_scheme get_allowed_fields called")

        # Ensure one
        self.ensure_one()

        # Initialize list
        result = []

        # Get linked model configuration
        model_configuration = self.model_whitelist.filtered(lambda x: x.model_name == model_name)

        if model_configuration:
            result = model_configuration.get_allowed_fields(request_field_list)

        self._write_to_debug_log("get_allowed_fields result", result)
        # Return
        return result

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
