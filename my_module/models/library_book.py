from odoo import models, fields
from odoo import api # if not already imported
from odoo.fields import Date as fDate
from datetime import timedelta
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    name = fields.Char('Título', required=True)
    date_release = fields.Date('Fecha de Lanzamiento')
    author_ids = fields.Many2many('res.partner', string='Autores')
    publisher_id = fields.Many2one('res.partner', string='Publicación',
                                    ondelete='set null', context={}, domain=[])
    currency_id = fields.Many2one('res.currency', string='Moneda')
    retail_price = fields.Monetary('Precio de Venta', currency_field='currency_id')


###################################################################
#     PARA CAMPOS CON VALIDACIONES EN LA BASE DE DATOS
#    _sql_constraints = [('name_uniq', 'UNIQUE (name)', 'El título del libro debe ser único.')]
#    @api.constrains('date_release')
#    def _check_release_date(self):
#        for record in self:
#            if (record.date_release and
#            record.date_release >fields.Date.today()):
#            raise models.ValidationError('Release date must be in the past')
###################################################################

###################################################################
#     PARA CAMPOS COMPUTADOS
    age_days = fields.Float(string='Dias desde la publicación',
                            compute='_compute_age',
                            inverse='_inverse_age',
                            search='_search_age',
                            store=False,
                            compute_sudo=False)
    @api.depends('date_release')
    def _compute_age(self):
        today = fDate.from_string(fDate.today())
        for book in self.filtered('date_release'):
            delta = (today -
            fDate.from_string(book.date_release))
            book.age_days = delta.days
    def _inverse_age(self):
        today = fDate.from_string(fDate.context_today(self))
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = fDate.to_string(d)
    def _search_age(self, operator, value):
        today = fDate.from_string(fDate.context_today(self))
        value_days = timedelta(days=value)
        value_date = fDate.to_string(today - value_days)
        # convert the operator:
        # book with age >value have a date <value_date
        operator_map = {
        '>': '<', '>=': '<=',
        '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]
###################################################################
#      PARA USO DE UN BOTON
    state = fields.Selection([('draft', 'Unavailable'),
                             ('available', 'Available'),
                             ('borrowed', 'Borrowed'),
                             ('lost', 'Lost')],
                             'State')
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
        ('available', 'borrowed'),
        ('borrowed', 'available'),
        ('available', 'lost'),
        ('borrowed', 'lost'),
        ('lost', 'available')]
        return (old_state, new_state) in allowed
    #@api.multi
    @api.model
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                continue
##################################################################
#      METODO PARA CREAR UN NUEVO REGISTRO
#    def some_method(self):
#        today_str = fields.Date.context_today(self)
#        val1 = {'name': 'Luis Millan',
#                'email': 'lmillan131@gmail.com'
#                'date': today_str}
#        val2 = {'name': 'John Cleese',
#                'email': 'john.cleese@example.com',
#                'date': today_str}
#        partner_val = {'name': 'Flying Circus',
#                        'email': 'm.python@example.com',
#                        'date': today_str,
#                        'is_company': True,
#                        'child_ids': [(0, 0, val1), (0, 0, val2),]}
#        record = self.env['res.partner'].create(partner_val)
##################################################################
class ResPartner(models.Model):
    _inherit = 'res.partner'
    published_book_ids = fields.One2many('library.book', 'publisher_id',
                                         string='Published Books')
    authored_book_ids = fields.Many2many('library.book',string='Authored Books',
                                         relation='library_book_res_partner_rel')

    #notes = fields.Text('Internal Notes')
    #state = fields.Selection([('draft', 'Not Available'), ('available', 'Available'), ('lost', 'Lost')], 'State')
    #description = fields.Html('Description')
    #cover = fields.Binary('Book Cover')
    #out_of_print = fields.Boolean('Out of Print?')
    #date_release = fields.Date('Release Date')
    #date_updated = fields.Datetime('Last Updated')
    #pages = fields.Integer('Number of Pages')
    #reader_rating = fields.Float('Reader Average Rating',digits=(14, 4))
