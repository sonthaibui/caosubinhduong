from odoo import api, fields, models,exceptions


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        for invoice in self:
            if invoice.journal_id and not invoice.journal_id.restrict_mode_hash_table:
                invoice.journal_id.write({'restrict_mode_hash_table':True})
            return super(AccountInvoice,self).button_cancel()
