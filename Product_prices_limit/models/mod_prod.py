#-*- coding: utf-8 -*-
from odoo import models, fields, api
class Prices_product(models.Model):
    _inherit ='product.pricelist'
    security_groups = fields.Many2one('res.groups', 'security groups')
