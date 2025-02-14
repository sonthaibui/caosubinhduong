# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    qty_used = fields.Float(string='Quantity Used',default=0.0,store=True,compute='_compute_quantity')
    qty_on_lot_seri = fields.Float(string='Quantity in Lot/Seria',store=True,compute='_compute_quantity')

    sale_line_ids = fields.One2many('sale.order.line', 'lot_sn_id')

    @api.depends('sale_line_ids.order_id.state', 'sale_line_ids.product_uom_qty')
    def _compute_quantity(self):
        for line in self:
            qty_used =  0
            qty_remain = line.product_qty
            sale_lines = line.sale_line_ids.filtered(lambda x: x.order_id.state != 'cancel')
            if sale_lines:
                qty_used = sum(sale_lines.mapped('product_uom_qty'))
                qty_remain -= qty_used

            line.write({
                'qty_used': qty_used,
                'qty_on_lot_seri': qty_remain,
            })

    @api.constrains('qty_used')
    def _check_qty_used(self):
        if self.filtered(lambda l: l.qty_used and l.qty_used > l.product_qty):
            raise ValidationError(_("Quantity to Sale do not more than quantity demanded."))
            