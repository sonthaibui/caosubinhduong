from odoo import models, fields

class KanbanState(models.Model):
    _name = 'kanban.state'
    _description = 'Kanban State'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)