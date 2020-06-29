# -*- coding: utf-8 -*-
# 1 : imports of python lib
import logging

# 2 : imports of odoo
from odoo import _, api, exceptions, fields, models, tools  # alphabetically ordered

# 3 : imports from odoo modules

# 4 : variable declarations
_logger = logging.getLogger(__name__)


# Class
class OregionalRestapiApplicationUri(models.Model):
    # Private attributes
    _name = 'oregional.restapi.application.uri'
    _description = "REST API application URI"
    _inherit = ['mail.thread']
    _order = 'uri'

    # Default methods

    # Fields declaration
    active = fields.Boolean(
        default=True,
        string="Active",
        track_visibility='onchange',
    )
    application = fields.Many2one(
        comodel_name='oregional.restapi.application',
        index=True,
        required=True,
        string="Application",
    )
    authorize_individually = fields.Boolean(
        default=False,
        help="The URI must be authorized individually by the user",
        string="Authorize Individually",
    )
    uri = fields.Char(
        required=True,
        string="URI",
        track_visibility='onchange',
    )
    description = fields.Text(
        help="Additional information",
        string="Description",
        translate=True,
        track_visibility='onchange',
    )

    # Compute and search fields, in the same order of fields declaration

    # Constraints and onchanges

    # CRUD methods (and name_get, name_search, ...) overrides
    # # Override create
    @api.model
    def create(self, values):
        # Check if name already exists
        if values.get('uri'):
            existing = self.env['oregional.restapi.application.uri'].search([
                ('uri', '=', values['uri'])
            ])
            if existing:
                raise exceptions.UserError(_("Uri is already registered for an application!"))

        # Execute create
        return super(OregionalRestapiApplicationUri, self).create(values)

    # # Override name_get
    @api.multi
    def name_get(self):
        # Initialize result
        result = []

        # Iterate through self
        for item in self:
            # Set name to uri name
            name = item.uri

            # Append to list
            result.append((item.id, name))

        # Return
        return result

    # Action methods

    # Business methods
