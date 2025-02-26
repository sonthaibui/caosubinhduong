# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ['stock.move', 'mail.thread']

    qty_accumulated = fields.Float('Quantity Accumulated', store=True)

    def _action_done(self,cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)
        for each_move in res:
            each_move.qty_accumulated = self.env['stock.quant']._get_inventory_quantity(each_move.product_id,each_move.location_dest_id)
        return res
