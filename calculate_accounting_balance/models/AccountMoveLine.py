import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ngay = fields.Integer('Ngay', compute='_compute_ntq', store=True, copy=True)
    thang = fields.Char('Thang', compute='_compute_ntq', store=True, copy=True)
    quy = fields.Char('Quy', compute='_compute_ntq', store=True, copy=True)
    stock_move_id = fields.Many2one('stock.move', related='move_id.stock_move_id', string='Stock Move')
    giamdoc_duyet = fields.Boolean('GĐ Duyệt', store=True, copy=True)
    ketoan_duyet = fields.Boolean('KT Duyệt', store=True, copy=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)
        
    @api.depends('date')
    def _compute_ntq(self):
        for rec in self:
            if rec.date:
                rec.ngay = rec.date.timetuple().tm_yday
                thang = rec.date.month
                if thang < 10:
                    rec.thang = "Tháng 0" + str(thang)
                else:
                    rec.thang = "Tháng " + str(thang)
                rec.quy = "Quý " + str(math.ceil(rec.date.month / 3))