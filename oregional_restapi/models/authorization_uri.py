# -*- coding: utf-8 -*-
# 1 : imports of python lib
import logging

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models, tools  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations:
_logger = logging.getLogger(__name__)


# Class
class OregionalRestapiAuthorizationUri(models.Model):
    # Private attributes
    _name = 'oregional.restapi.authorization.uri'
    _description = "REST API authorization uri"

    # Default methods

    # Field declarations
    application = fields.Many2one(
        comodel_name='oregional.restapi.application',
        help="Related application",
        related='authorization.application',
        string="Application",
    )
    authorization = fields.Many2one(
        comodel_name='oregional.restapi.authorization',
        help="Linked authorization",
        index=True,
        ondelete='cascade',
        required=True,
        string="Authorization",
    )
    uri = fields.Char(
        help="Authorized URI of the remote application",
        required=True,
        string="URI",
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides

    # Action methods

    # Business methods
