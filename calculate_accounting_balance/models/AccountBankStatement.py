import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    giamdoc_duyet = fields.Boolean('Giám Đốc Duyệt', store=True, copy=True, tracking=True)
    ketoan_duyet = fields.Boolean('Kế Toán Duyệt', store=True, copy=True, tracking=True)
    ketoan_trang = fields.Boolean('KT Trang', store=True, copy=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    ghi_chu = fields.Char('Ghi Chú', tracking=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Tổ', store=True, copy=True, tracking=True)

    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.depends('previous_statement_id', 'previous_statement_id.balance_end_real')
    def _compute_ending_balance(self):
        super()._compute_ending_balance()
        latest_statement = self.env['account.bank.statement'].search([('journal_id', '=', self[0].journal_id.id)], limit=1)
        for statement in self:
            if statement.journal_type == 'cash':
                if latest_statement.id and statement.id == latest_statement.id and not float_is_zero(statement.balance_end_real, precision_digits=statement.currency_id.decimal_places):
                    statement.balance_end_real = statement.balance_end_real or 0.0
                else:
                    total_entry_encoding = sum([line.amount for line in statement.line_ids])
                    statement.balance_end_real = statement.previous_statement_id.balance_end_real + total_entry_encoding

    @api.onchange('analytic_id')
    def _onchange_analytic_id(self):
        if self.analytic_id:
            if len(self.line_ids) > 0:
                for line in self.line_ids:
                        line.phantich_id = self.analytic_id.id
        else:
            if len(self.line_ids) > 0:
                for line in self.line_ids:
                        line.phantich_id = False
    
    @api.onchange('balance_end')
    def _onchange_balance_end(self):
        self.balance_end_real = self.balance_end
        asts = self.env['account.bank.statement']
        for st in asts:
            if st.id > self._origin.id:
                st.balance_end = st.balance_start + st.total_entry_encoding

    def copy(self):
        vals = super(AccountBankStatement, self).copy()
        vals.giamdoc_duyet = False
        vals.ketoan_duyet = False
        for line in vals.line_ids:
            line.ketoan_duyet = False
            line.giamdoc_duyet = False
        #raise UserError(_(vals.giamdoc_duyet))
        return vals