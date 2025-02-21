import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    taikhoan_id = fields.Many2one('account.account', string='Tai Khoan', store=True)
    phantich_id = fields.Many2one('account.analytic.account', string='Tổ', store=True)
    giamdoc_duyet = fields.Boolean('GĐ Duyệt', store=True, copy=True)
    ketoan_duyet = fields.Boolean('KT Duyệt', store=True, copy=True)
    ketoan_trang = fields.Boolean('KT Trang', store=True, copy=True)
    nguoitao = fields.Char(related='statement_id.nguoitao')
    ghi_chu = fields.Char('Ghi Chú', store=True, copy=True)
    #bill_id = fields.Many2one('account.move', string='Bill')#, domain=['|',('payment_state','=','not_paid'),('payment_state','=','partial')])

    """ @api.onchange('bill_id')
    def _onchange_bill_id(self):
        for rec in self:
            if rec.partner_id:
                return {'domain': {'bill_id': [('invoice_partner_display_name', '=', rec.partner_id.name),'|',('payment_state','=','not_paid'),('payment_state','=','partial')]}}
 """
    @api.model
    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        [liquidity_line_vals, counterpart_line_vals] = super()._prepare_move_line_default_vals()
        if self.taikhoan_id:
            counterpart_account_id = self.taikhoan_id.id
            counterpart_line_vals.update({'account_id': counterpart_account_id})
        if self.phantich_id:
            counterpart_line_vals['analytic_account_id'] = self.phantich_id.id
        return [liquidity_line_vals, counterpart_line_vals]
    
    @api.onchange('taikhoan_id', 'phantich_id')
    def _onchange_taikhoan_id(self):
        if self.payment_ref:
            label = self.payment_ref
            lastchar = label[-1]
            if lastchar == '.':
                self.payment_ref = label[:-1]
            else:
                self.payment_ref = label + '.'

    @api.onchange('ghi_chu')
    def _onchange_ghi_chu(self):
        if self.ghi_chu:
            statement_id = self.env['account.bank.statement'].search([('journal_id','=',self.statement_id.journal_id.id)])
            notification_ids = []
            notification_ids.append((0, 0, {
                'res_partner_id': self.env['res.users'].browse(41).partner_id.id,
                'notification_type': 'inbox'
            }))
            self.env['mail.message'].create(
                {
                    'message_type': 'notification',
                    'body': self.payment_ref + ': ' + self.ghi_chu,
                    'subject': statement_id[0].name + statement_id[0].journal_id.name,
                    'partner_ids': [(4, self.env['res.users'].browse(41).partner_id.id)],
                    'model': self._name,
                    'subtype_id': self.env.ref("mail.mt_comment").id,
                    'res_id': self.id,
                    'author_id': self.env.user.partner_id and self.env.user.partner_id.id,
                    'notification_ids': notification_ids,
                }
            )

    @api.model
    def create(self, vals):
        res = super(AccountBankStatementLine, self).create(vals)
        if res.statement_id.analytic_id:
            res.phantich_id = res.statement_id.analytic_id.id
        return res