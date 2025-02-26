import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    valuation = fields.Float(compute='_compute_valuation', string='Valuation')
    #manual_cost = fields.Float('Manual Cost', related='move_id.manual_cost')
    #manual_valuation = fields.Float('Manual Valuation', related='move_id.manual_valuation')
    account_move_id = fields.Many2one('account.move', compute='_compute_valuation', string='Account Move')
    source = fields.Float('Source', compute='_compute_cumulative')
    dest = fields.Float('Dest', compute='_compute_cumulative')

    @api.depends('move_id','product_id')
    def _compute_valuation(self):
        for record in self:
            if self.env['account.move.line'].search([('stock_move_id','=',record.move_id.id),('product_id','=',record.product_id.id)]) and record.location_id.name != 'Inventory adjustment':
                ams = self.env['account.move.line'].search([('stock_move_id','=',record.move_id.id),('product_id','=',record.product_id.id)])
                record.valuation = abs(ams[0].balance)
                record.account_move_id = ams[0].move_id.id
            else:
                record.valuation = 0
                record.account_move_id = None

    @api.depends('product_id')
    def _compute_cumulative(self):
        for rec in self:
            rec.source = 0
            rec.dest = 0
            sml = self.env['stock.move.line'].search([('product_id','=',rec.product_id.id),('state', '=', 'done')])
            sml = sml.sorted(key=lambda r: (r.date, r.id))
            cumulative = {}
            for line in sml:
                if cumulative.get(line.location_id.id) is None:
                    cumulative[line.location_id.id] = 0
                if cumulative.get(line.location_dest_id.id) is None:
                    cumulative[line.location_dest_id.id] = 0
                s = cumulative[line.location_id.id]
                cumulative[line.location_id.id] = s - line.qty_done
                line.source = cumulative[line.location_id.id]
                d = cumulative[line.location_dest_id.id]
                cumulative[line.location_dest_id.id] = d + line.qty_done
                line.dest = cumulative[line.location_dest_id.id]