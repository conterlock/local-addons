#-*- coding: utf-8 -*-
class Prices_product(models.Model):
    _inherit ='product.pricelist'
    security_groups = fields.Many2one('res.groups', 'security groups')
