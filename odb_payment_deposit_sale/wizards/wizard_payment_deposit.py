from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PaymentOrderDepositWizard(models.TransientModel):
    _inherit = "payment.order.deposit.wizard"

    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale Order', ondelete='set null')

    # @api.constrains("amount_advance")
    def check_amount(self):
        if self.env.context.get("active_id", False):
            self.onchange_payment_deposit()
            if float_compare(self.amount_remain, self.sale_id.deposit_remain, precision_digits=2) > 0:
                raise exceptions.ValidationError(_("Amount of advance is greater than residual amount on sale"))
        return super(PaymentOrderDepositWizard, self).check_amount()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_ids = self.env.context.get("active_ids", [])
        if not sale_ids:
            return res
        sale_id = fields.first(sale_ids)
        sale = self.env["sale.order"].browse(sale_id)
        if "amount_total" in fields_list:
            res.update({
                "sale_id": sale.id,
                "amount_total": sale.amount_total - sum(sale.payment_deposit_ids.mapped('amount_advance')),
                "currency_id": sale.pricelist_id.currency_id.id,
            })
        return res

    def _prepare_sale_payment_deposit_vals(self, sale):
        if self.amount_advance <= 0.0:
            raise UserError(_("The amount to advance must always be positive. Please use the payment type to indicate if thisis an inbound or an outbound payment."))
        return {
            "name": self.name,
            "sale_id": self.sale_id.id,
            "amount_total": self.amount_total,
            "amount_advance": self.amount_advance,
            "amount_remain": self.amount_remain,
            "payment_type": self.payment_type,
            "payment_ref": self.payment_ref,
            "journal_id": self.journal_id.id,
            "currency_id": self.journal_currency_id.id,
            "partner_id": sale.partner_invoice_id.commercial_partner_id.id,
            "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
            "description": self.description
        }

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        deposit_obj = self.env["payment.order.deposit"]
        sale_id = self.env["sale.order"].browse(self.env.context.get("active_id", False))
        if sale_id:
            payment_vals = self._prepare_sale_payment_deposit_vals(sale_id)
            deposit_obj.create(payment_vals)
        return super(PaymentOrderDepositWizard, self).make_advance_payment()