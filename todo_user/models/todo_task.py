from odoo import models, fields, api
class TodoTask(models.Model):
    _inherit = 'todo.task'
    user_id = fields.Many2one('res.users', 'Responsible')
    date_deadline = fields.Date('Deadline')
    name = fields.Char(help="What needs to be done?")
    
    @api.model
    def do_clear_done(self):
        domain = [('is_done', '=', True), '|', ('user_id', '=', self.env.uid), ('user_id', '=', False)]
        done_recs = self.search(domain)
        done_recs.write({'active': False})
        return True
