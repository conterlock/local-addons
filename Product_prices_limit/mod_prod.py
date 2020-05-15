#   Módulo para limitación de acceso a precios y tarifas en productos odoo
#   Yarnabeth
#   Autor: Luis Millan
from odoo import models, fields, api

################################################################################
#   Para limitación de precios propios de los productos                        #
################################################################################
#class Productos(models.Model):
#    _inherit = 'product.product'
    #list_price = fields.Float(groups="group_sale_manager.group_user")       # Precio de Venta
    #lst_price = fields.Float(groups="group_sale_manager.group_user")        # Precio al Público
    #price = fields.Float(groups="group_sale_manager.group_user")            # Precio
    #price_extra = fields.Float(groups="group_sale_manager.group_user")      # Precio adicional
    #standard_price = fields.Float(groups="sales_team.group_sale_manager")   # Coste

#class Productos_template(models.Model):
#    _inherit = 'product.template'
    #list_price = fields.Float(groups="group_sale_manager.group_user")       # Precio de Venta
    #lst_price = fields.Float(groups="group_sale_manager.group_user")        # Precio al Público
    #price = fields.Float(groups="group_sale_manager.group_user")            # Precio
    #standard_price = fields.Float(groups="sales_team.group_sale_manager")   # Coste

################################################################################
#   Para limitación de Tarifas por grupos asociados                            #
################################################################################
class Prices_product(models.Model):
    _inherit ='product.pricelist'
    group_id = fields.Char('ID grupo', default='no_group')      # ID externo de grupo asociado a la tarifa
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
