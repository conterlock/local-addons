#-*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
class Sale_order_copy(models.Model):
    _inherit ='sale.order'
    is_copy = fields.Boolean('Copiado?', default=False)

    def do_copy_sale_order(self):
        ###################################################
        # Parámetros de Conexión entre Instancias de Odoo #
        ###################################################
        if self.is_copy == False:
            common = xmlrpc.client.ServerProxy('http://172.17.0.1:8070/xmlrpc/2/common')    # Conexión
            uid = common.authenticate('OdooDB', 'lmillan131@gmail.com', '1123581321', {})   # Autenticación
            models = xmlrpc.client.ServerProxy('http://172.17.0.1:8070/xmlrpc/2/object')    # Modelo para la conexión

            ###################################################
            # Generación de nuevos registros necesarios       #
            ###################################################
            order = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'create',  # Nuevo Pedido de Venta
                [{'partner_id': 1, 'pricelist_id':1,}])
            for f in self.env['sale.order.line'].search([('order_id', '=', self.name)]):
                producto = self.env['product.product'].search([('product_variant_id', '=', f.product_id)])
                clave = producto.default_code
                order_line_copy = models.execute_kw('OdooDB', uid, '1123581321',            # Nueva Linea de Pedido
                'sale.order.line', 'create', [{'order_id': order, 'product_id': 1, 'product_uom_qty': 1}])
            self.is_copy = True
