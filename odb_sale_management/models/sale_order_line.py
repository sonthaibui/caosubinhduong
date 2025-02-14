# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commitment_date = fields.Datetime("Commitment Date", default=fields.Date.context_today)
    categ_id = fields.Many2one('product.category','Category')
    date_order = fields.Datetime("Date Order", related='order_id.date_order')
    qty_on_hand = fields.Float(string='Qty on Hand', related='product_id.qty_available')
    journal_id = fields.Many2one("account.journal", "Payment Method", related='order_id.journal_id')
    product_qty = fields.Float(string='Quantity Real', compute='_compute_product_qty', digits=0, store=True,  compute_sudo=True, default=0)
    note = fields.Text(string='Note')
    sanluong = fields.Float(string='Sản Lượng')
    do = fields.Float(string='Độ')
    ngay = fields.Integer('Ngay', compute='_compute_ntq', store=True, copy=True)
    thang = fields.Char('Thang', compute='_compute_ntq', store=True, copy=True)
    quy = fields.Char('Quy', compute='_compute_ntq', store=True, copy=True)
    
    @api.depends('commitment_date')
    def _compute_ntq(self):
        for rec in self:
            if rec.commitment_date:
                rec.ngay = rec.commitment_date.timetuple().tm_yday
                thang = rec.commitment_date.month
                if thang < 10:
                    rec.thang = "Tháng 0" + str(thang)
                else:
                    rec.thang = "Tháng " + str(thang)
                rec.quy = "Quý " + str(math.ceil(rec.commitment_date.month / 3))

    @api.onchange('sanluong', 'do')
    def onchange_sanluong_do(self):
        self.product_uom_qty = self.sanluong * (self.do / 100)

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('product_uom_qty', 'product_id','product_uom')
    def _compute_product_qty(self):
        for line in self:
            line.product_qty = line.product_id and line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id, rounding_method='HALF-UP') or 0

    def write(self, vals):
        # Force commitment date only if all lines are on the same sale order
        if len(self.mapped("order_id")) == 1:
            for line in self:
                if not line.commitment_date and line.order_id.commitment_date and "commitment_date" not in vals:
                    vals.update({"commitment_date": line.order_id.commitment_date})
                    break
        return super(SaleOrderLine, self).write(vals)

    def action_custom(self):
        res_id = self.env['component.attribute'].search([('sale_order_line','=',self.id)]).id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'component.attribute',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': res_id,
            'target': 'new',
        }