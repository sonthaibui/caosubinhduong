from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_cancel(self):
        for rec in self:
            # cancel invoice
            for inv in rec.invoice_ids:
                if inv.state != 'cancel':inv.button_cancel()
            # cancel picking done
            for line in rec.picking_ids:
                if line.state !='cancel': line.action_cancel()
            return super(PurchaseOrder, self).button_cancel()


            
