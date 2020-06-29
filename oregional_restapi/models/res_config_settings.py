# -*- coding: utf-8 -*-
# 1 : imports of python lib

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations


# Class
class OregionalRestApiResConfigSettings(models.TransientModel):
    # Private attributes
    _inherit = 'res.config.settings'

    # Default methods

    # Fields declaration
    oregional_rest_api_is_debug_mode = fields.Boolean(
        string="REST API debug mode",
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides

    # Action methods

    # Business methods
    @api.multi
    def get_values(self):
        res = super(OregionalRestApiResConfigSettings, self).get_values()
        res.update(
            oregional_rest_api_is_debug_mode=self.env['ir.config_parameter'].sudo().get_param('oregional_restapi.oregional_rest_api_is_debug_mode')
        )
        return res

    def set_values(self):
        super(OregionalRestApiResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('oregional_restapi.oregional_rest_api_is_debug_mode', self.oregional_rest_api_is_debug_mode)
