import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class AccountMove(models.Model):
    _inherit = "account.move"

    giamdoc_duyet = fields.Boolean('Giám Đốc Duyệt', store=True, copy=True, tracking=True)
    ketoan_duyet = fields.Boolean('Kế Toán Duyệt', store=True, copy=True, tracking=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.invoice_has_outstanding == True:
            aml = self.env['account.move.line'].search([('move_id','=',self.id)])
            for am in aml:
                if not am.analytic_account_id:
                    am.analytic_account_id = aml[0].analytic_account_id
        return True
    
    def copy(self):
        vals = super(AccountMove, self).copy()
        vals.giamdoc_duyet = False
        vals.ketoan_duyet = False
        
        #line.giamdoc_duyet = False
        #raise UserError(_(vals.giamdoc_duyet))
        return vals
