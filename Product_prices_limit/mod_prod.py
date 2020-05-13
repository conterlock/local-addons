#   Módulo para limitación de acceso a precios y tarifas en productos odoo
#   Yarnabeth
#   Autor: Luis Millan
from odoo import models, fields, api

################################################################################
#   Para limitación de precios propios de los productos                        #
################################################################################
class Productos(models.Model):
    _inherit = 'product.product'
    #list_price = fields.Float(groups="group_sale_manager.group_user")       # Precio de Venta
    #lst_price = fields.Float(groups="group_sale_manager.group_user")        # Precio al Público
    #price = fields.Float(groups="group_sale_manager.group_user")            # Precio
    #price_extra = fields.Float(groups="group_sale_manager.group_user")      # Precio adicional
    #standard_price = fields.Float(groups="sales_team.group_sale_manager")   # Coste

class Productos_template(models.Model):
    _inherit = 'product.template'
    #list_price = fields.Float(groups="group_sale_manager.group_user")       # Precio de Venta
    #lst_price = fields.Float(groups="group_sale_manager.group_user")        # Precio al Público
    #price = fields.Float(groups="group_sale_manager.group_user")            # Precio
    #standard_price = fields.Float(groups="sales_team.group_sale_manager")   # Coste

################################################################################
#   Para limitación de Tarifas por grupos asociados                            #
################################################################################
class Prices_product(models.Model):
    _inherit ='product.pricelist'
    group_id = fields.Char('ID grupo')      # ID externo de grupo asociado a la tarifa
