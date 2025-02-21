from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    trangthai_id = fields.Many2one('trangthai', string='Trạng thái', store=True)
class TrangThai(models.Model):
    _name = 'trangthai'
    _description = 'TrangThai'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)