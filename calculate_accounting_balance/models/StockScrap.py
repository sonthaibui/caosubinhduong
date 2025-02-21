import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    date_done = fields.Datetime(readonly=False)
    inter_date  = fields.Datetime('Date', readonly=True)
    note = fields.Char('Note')

    def do_scrap(self):
        for scrap in self:
            scrap.inter_date = scrap.date_done
        super(StockScrap, self).do_scrap()
        for scrap in self:
            scrap.date_done = scrap.inter_date
            scrap.move_id.date = scrap.inter_date
    
    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                rec.state = 'draft'
                self.env['stock.move'].browse(rec.move_id.id).state = 'cancel'
                quant_obj= self.env['stock.quant']
                quantity = rec.product_uom_id._compute_quantity(rec.scrap_qty, rec.product_id.uom_id)
                quant_obj._update_available_quantity(rec.product_id, rec.location_id, quantity, rec.lot_id)
                quant_obj._update_available_quantity(rec.product_id, rec.scrap_location_id, quantity * -1 ,rec.lot_id)

