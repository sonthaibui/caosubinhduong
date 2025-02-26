from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PaymentOrderDepositWizard(models.TransientModel):
    _name = "payment.order.deposit.wizard"
    _description = "Payment Order Deposit Wizard"

    name = fields.Date("Date", required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one("account.journal", "Journal", required=True, domain=[("type", "in", ("bank", "cash"))])
    currency_id = fields.Many2one("res.currency", "Currency")
    journal_currency_id = fields.Many2one("res.currency", "Journal Currency", store=True, readonly=False, compute="_compute_get_journal_currency")
    amount_total = fields.Monetary("Amount total", currency_field="journal_currency_id")
    amount_advance = fields.Monetary("Down Payment", currency_field="journal_currency_id", compute='onchange_payment_deposit')
    amount_remain = fields.Monetary("Balance", currency_field="currency_id", compute='onchange_payment_deposit')
    compute_type = fields.Selection([
            ('percent', 'Percent'),
            ('fix', 'Fix Price'),
        ], string='Compute Type', default='percent')
    payment_ref = fields.Char("Ref.")
    payment_type = fields.Selection([("inbound", "Inbound"), ("outbound", "Outbound")], default="inbound", required=True)
    value = fields.Float(string='Value', default=0.0, required=True)
    description = fields.Char(string='Description',)

    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = wzd.journal_id.currency_id.id or wzd.journal_id.company_id.currency_id.id

    # @api.constrains("amount_advance")
    def check_amount(self):
        if self.value <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be positive."))
    
    @api.depends("journal_id", "value", "compute_type")
    def onchange_payment_deposit(self):
        if self.value == 0.0:
            self.update({
                    'amount_advance': 0.0,
                    'amount_remain': 0.0
                })
        elif self.value > 0:
            amount_advance = 0.0
            amount_remain = 0.0
            if self.compute_type == 'percent':
                amount_advance = self.amount_total / 100 * self.value
            elif self.compute_type == 'fix':
                amount_advance = self.value
            if self.journal_currency_id != self.currency_id:
                amount_advance = self.journal_currency_id._convert(self.amount_advance, self.currency_id,
                    self.sale_id.company_id, self.name or fields.Date.today())
            if amount_advance > 0.0:
                self.write({
                    'amount_advance': amount_advance,
                    'amount_remain': self.amount_total - amount_advance
                })

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        return {"type": "ir.actions.act_window_close"}