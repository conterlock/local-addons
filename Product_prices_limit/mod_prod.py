from odoo import models, fields

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

class Prices_product(models.Model):
    _inherit ='product.pricelist'
    product_prices_group = fields.Integer('ID grupo', default=0)
