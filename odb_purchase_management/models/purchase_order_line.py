# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    note = fields.Text(string='Note')

    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', compute='_compute_invoice_status', store=True, readonly=True, copy=False, default='no')

    @api.depends('state','qty_to_invoice')
    def _compute_invoice_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('purchase', 'done'):
                line.invoice_status = 'no'
            elif not line.display_type and not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif not line.display_type and float_is_zero(line.qty_to_invoice, precision_digits=precision) and line.order_id.invoice_ids:
                # if line.check_invoice_posted() == True:
                line.invoice_status = 'invoiced'
                # else:
                #    line.invoice_status = 'to invoice' 
            else:
                 line.invoice_status = 'no'

    # def check_invoice_posted(self):
    #     for rec in self.order_id.invoice_ids.invoice_line_ids:
    #         if rec.
