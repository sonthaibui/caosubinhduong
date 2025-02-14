from odoo import api, fields, models,exceptions
from odoo.tools.float_utils import float_round, float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        for rec in self:
        # cancel invoice
            for inv in rec.invoice_ids:
                if inv.state != 'cancel':inv.button_cancel()
        # cancel picking done
            for line in rec.picking_ids:
                if line.state !='cancel': line.action_cancel()
            return super(SaleOrder,self).action_cancel()
