from odoo import api, fields, models, _

class TreeLine(models.Model):
    _name = 'tree.line'
    _description = 'Tree Line Model'

    stt = fields.Integer('STT')
    o = fields.Integer('O')
    k = fields.Integer('K')
    km = fields.Integer('KM')
    g = fields.Integer('G')
    tong = fields.Integer('Tổng')
    plantation_id = fields.Many2one('plantation', string='Phần Cây', ondelete='cascade')
    nongtruong = fields.Selection(related='plantation_id.nongtruong')
    toname = fields.Char('Tổ', related='plantation_id.to.name')
    loso = fields.Char('Lô Số')
    lo = fields.Selection(related='plantation_id.lo')
    ghi_chu = fields.Text('Ghi Chú')
