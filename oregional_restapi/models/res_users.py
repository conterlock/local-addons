# -*- coding: utf-8 -*-
# 1 : imports of python lib

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models, tools  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations:


# Class
class OregionalRestapiResUsers(models.Model):
    # Private attributes
    _inherit = 'res.users'

    # Default methods

    # Field declarations
    oregional_restapi_authorization = fields.One2many(
        comodel_name='oregional.restapi.authorization',
        inverse_name='user',
        index=True,
        string="Authorization",
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides

    # Action methods

    # Business methods

