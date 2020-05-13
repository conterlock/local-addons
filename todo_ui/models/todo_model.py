from odoo import models, fields, api

class Tag(models.Model):
    _name         = 'todo.task.tag'
    _parent_store = True
    #_parent_name  = 'parent_id'
    name = fields.Char('Name')
    parent_id     = fields.Many2one('todo.task.tag','Parent Tag', ondelete='restrict')
    parent_left   = fields.Integer('Parent Left', index=True)
    parent_right  = fields.Integer('Parent  Right', index=True)
    child_ids = fields.One2many('todo.task.tag', 'parent_id', 'Child Tags')

class Stage(models.Model):
    _name  = 'todo.task.stage'
    _order = 'sequence,name'

    # Campos de cadena de caracteres:
    name  = fields.Char('Name',40)
    desc  = fields.Text('Description')
    state = fields.Selection([('draft','New'),('open','Started'), ('done','Closed')],'State')
    docs  = fields.Html('Documentation')

    # Campos numéricos:
    sequence      = fields.Integer('Sequence')
    perc_complete = fields.Float('% Complete',(3,2))

    # Campos de fecha:
    date_effective = fields.Date('Effective Date')
    date_changed   = fields.Datetime('Last Changed')

    # Otros campos:
    fold  = fields.Boolean('Folded?')
    image = fields.Binary('Image')

class TodoTask(models.Model):
    _inherit = 'todo.task'
    stage_id = fields.Many2one('todo.task.stage', 'Stage')
    tag_ids = fields.Many2many('todo.task.tag', string='Tags')
