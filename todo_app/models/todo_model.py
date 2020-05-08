from odoo import models, fields

class TodoTask(models.Model):
    _name = 'todo.task'
    name = fields.Char('Descripción', required=True)
    is_done = fields.Boolean('¿Listo?')
    active = fields.Boolean('¿Activo?', default=True)
