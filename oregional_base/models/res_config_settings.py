# -*- coding: utf-8 -*-
# 1 : imports of python lib

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations


# Class
class OregionalBaseResConfigSettings(models.TransientModel):
    # Private attributes
    _inherit = 'res.config.settings'

    # Default methods

    # Fields declaration
    group_oregional_app_admin = fields.Boolean(
        default=True,
        string="System admins are app admins",
        group='base.group_system',
        implied_group='oregional_base.group_app_admin',
    )
    is_installed_oregional_base = fields.Boolean(
        string="Base Oregional App is installed"
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides

    # Action methods

    # Business methods
    @api.multi
    def get_values(self):
        res = super(OregionalBaseResConfigSettings, self).get_values()
        res.update(
            is_installed_oregional_base=self.env['ir.module.module'].search([
                ('name', '=', 'oregional_base'),
                ('state', '=', 'installed')
            ]).id
        )
        return res

    def set_values(self):
        super(OregionalBaseResConfigSettings, self).set_values()
