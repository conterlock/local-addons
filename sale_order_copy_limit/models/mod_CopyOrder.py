#-*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
class Sale_order_copy(models.Model):
    _inherit ='sale.order'
    is_copy = fields.Boolean('Copiado?', default=False)

    def do_copy_sale_order(self):
        common = xmlrpc.client.ServerProxy('http://172.17.0.1:8070/xmlrpc/2/common')
        uid = common.authenticate('OdooDB', 'lmillan131@gmail.com', '1123581321', {})
        models = xmlrpc.client.ServerProxy('http://172.17.0.1:8070/xmlrpc/2/object')
        #id = models.execute_kw('OdooDB', uid, '1123581321', 'res.partner', 'create', [{'name': self.name,}])
        id = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'search_read', [[[1, '=', True]]], {'fields': ['name', 'company_id', 'currency_id', 'date_order', 'partner_id', 'partner_invoice_id', 'partner_shipping_id', 'picking_policy', 'pricelist_id', 'warehouse_id'], 'limit': 3})
        ser = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'fields_get',
            [], {'attributes': ['name', 'currency_id', 'date_order', 'partner_id', 'partner_invoice_id', 'pricelist_id']})
        id2 = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'create',
            [{'name': 'TO001',
              'currency_id': [4],
              'date_order': '2020-06-27 00:31:45',
              'partner_id': [14],
              'partner_invoice_id': [14],
              'partner_shipping_id': [14],
              'pricelist_id': [1]}])

        id3 = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'create', [{'partner_id': 1, 'pricelist_id':1}])


        #sale_copy = models.execute_kw('OdooDB', uid, '1123581321', 'sale.order', 'create', [{
        #    'name': self.name,
        #    'company_id': self.company_id
        #    'currency_id': self.currency_id
        #    'date_order': self.date_order
        #    'partner_id': self.partner_id
        #    'partner_invoice_id': self.partner_invoice_id
        #    'partner_shipping_id': self.partner_shipping_id
        #    'picking_policy': self.picking_policy
        #    'pricelist_id': self.pricelist_id
        #    'warehouse_id': self.warehouse_id
        #    }])
        self.is_copy = True
