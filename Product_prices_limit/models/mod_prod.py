
#-*- coding: utf-8 -*-
from odoo import models, fields, api
class Prices_product(models.Model):
    _inherit ='product.pricelist'
    group_id_sec = fields.Char('ID grupo', default='no_group')
    
#    group_limit = fields.Boolean(
#        string='Parte del Grupo',
#        compute="_compute_is_group_admin",
#    )
#
#    @api.depends('group_id')
#    def _compute_is_group_admin(self):
#        self.group_limit = self.env.user.has_group(self.group_id)
#        #['|', ('group_id', '=', False), (True, '=', user.has_group('group_id'))]
#
#
#class User_product(models.Model):
#    _inherit ='res.users'
#    list_groups_ids = fields.Char(compute = '_list_groups_ids')
#
#    @api.depends('groups_id')
#    def _list_groups_ids(self):
#        self.list_groups_ids = self.browse('groups_id')
