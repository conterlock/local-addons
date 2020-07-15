#-*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import xmlrpc.client
#class sale_param_copy(models.Model):
#    _inherit = 'res.config.settings'
#    DB = fields.Char('Base de Datos')
#    Password = fields.Char('Clave de Usuario')
#    User = fields.Char('Usuario')
#    url = fields.Char('Dirección URL')
class Sale_order_copy(models.Model):
    _inherit ='sale.order'
    is_copy = fields.Boolean('Copiado?', default=False)

    def do_copy_sale_order(self):
        ###################################################
        # Parámetros de Conexión entre Instancias de Odoo #
        ###################################################
        if self.is_copy == True:                                                        # Verifica que ha sido copiado
            message = _('El Pedido Seleccionado ya ha sido Copiado')
            raise UserError(message)

        try:
            DB = self.env['ir.config_parameter'].search([('key', '=', 'db.odoo11')]).value
            Password = self.env['ir.config_parameter'].search([('key', '=', 'password.odoo11')]).value
            User = self.env['ir.config_parameter'].search([('key', '=', 'user.odoo11')]).value
            url = self.env['ir.config_parameter'].search([('key', '=', 'url.odoo11')]).value
            print(DB, Password, User, url)
            common = xmlrpc.client.ServerProxy(url + 'xmlrpc/2/common')                 # Conexión
            uid = common.authenticate(DB, User, Password, {})                           # Autenticación
            models = xmlrpc.client.ServerProxy(url + 'xmlrpc/2/object')                 # Modelo para la conexión

        except:                                                                         # Abortar en caso de no conexión
            message2 = _('No se pudo establecer conexión, contacte al administrador')
            raise UserError(message2)

        ###################################################
        # Generación de nuevos registros necesarios       #
        ###################################################
        cliente = models.execute_kw(                                                    # Buscar Cliente
            DB, uid, Password, 'res.partner', 'search_read',
            [[['name', '=', self.partner_id.name]]],
            {'fields': ['name'], 'limit': 1})

        if cliente == []:                                                               # En caso de no existir, crear Cliente
            cliente_id = models.execute_kw(                                                # Crear Cliente
                DB, uid, Password, 'res.partner', 'create',
                [{
                    'name': self.partner_id.name,
                    'parent_name': self.partner_id.parent_name,
                    'contact_address': self.partner_id.contact_address,
                    'email': self.partner_id.email,
                    'phone': self.partner_id.phone
                }])
            #print('aqui el cliente recien creado:', cliente)
            #cliente = models.execute_kw(                                                # Id de nuevo Cliente
            #    DB, uid, Password, 'res.partner', 'search_read',
            #    [[['name', '=', self.partner_id.name]]],
            #    {'fields': ['name'], 'limit': 1})
            #print('aqui el formato para id:', cliente)
        else:
            cliente_id = cliente[0]['id']

        try:
            tarifa = models.execute_kw(                                                     # Busca Tarifa
                DB, uid, Password, 'product.pricelist', 'search_read'
                [[['name', '=', self.pricelist_id.name]]],
                {'fields': ['name'], 'limit': 1})
            print(tarifa)
            tarifa_id = tarifa[0]['id']
        except:
            print('no lee tarifa')
            tarifa_id = 1

        order = models.execute_kw(                                                      # Crea nuevo Pedido
            DB, uid, Password, 'sale.order', 'create',
            [{
                'partner_id': cliente_id,
                'pricelist_id': tarifa_id,
                'invoice_status': self.invoice_status,
                'date_order': self.date_order,
                'commitment_date': self.commitment_date,
                'amount_tax': self.amount_tax,
                'is_expired': self.is_expired
            }])

        try:
            for f in self.env['sale.order.line'].search([('order_id', '=', self.name)]):    # Bucle para crear lineas de pedido

                id_prod = models.execute_kw(                                                # Busca el ID del producto
                    DB, uid, Password, 'product.product', 'search_read',
                    [[['default_code', '=', f.product_id.default_code]]],
                    {'fields': ['default_code'], 'limit': 1})

                if f.tax_id.name != False:
                    impuesto = models.execute_kw(
                        DB, uid, Password, 'account.tax', 'search_read',
                        [[['name', '=', f.tax_id.name]]],
                        {'fields': ['name'], 'limit': 1})
                    impuesto_id = impuesto[0]['id']
                else:
                    impuesto_id = 1

                print('El impuesto es:', impuesto_id)

                order_line_copy = models.execute_kw(                                        # Crea una nueva linea de Pedido
                    DB, uid, Password, 'sale.order.line', 'create',
                    [{
                        'order_id': order,
                        'product_id': id_prod[0]['id'],
                        'product_uom_qty': f.product_uom_qty,
                        'tax_id': [impuesto_id]
                    }])
        except:
            message3 = _('Hay productos incompatibles entre versiones, contacte con el Administrador')
            models.execute_kw(
                DB, uid, Password, 'sale.order', 'unlink',
                [[order]])
            raise UserError(message3)
        self.is_copy = True                                                             # Cambiar estado de Copiado
