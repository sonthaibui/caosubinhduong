import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    backdate = fields.Date('Back Date', default=fields.Datetime.now(), required=True)
    #auto_cost = fields.Float('Auto Cost', compute='_compute_autocost')
    #manual_cost = fields.Float('Manual Cost', default="0")

    @api.model
    def _get_inventory_fields_write(self):
        fields = super(StockQuant, self)._get_inventory_fields_write()
        fields.append('backdate')
        #fields.append('auto_cost')
        #fields.append('manual_cost')
        return fields

    """ @api.depends('product_id')
    def _compute_autocost(self):
        for rec in self:
            rec.auto_cost = rec.product_id.product_tmpl_id.standard_price """

    def _apply_inventory(self):
        super(StockQuant, self)._apply_inventory()
        for rec in self:
            rec.inventory_date = rec.backdate
            sm = self.env['stock.move'].search([('location_dest_id', '=', rec.location_id.id),('location_id.name','=','Inventory adjustment')
            ,('product_id','=',rec.product_id.id)]) #,('product_uom_qty','=',rec.quantity)
            sm[len(sm) - 1].date = rec.backdate
            #if rec.quantity > 0:
                #rec.auto_cost = sm[len(sm) - 1].valuation / rec.quantity
            """ if rec.manual_cost > 0:
                sm[len(sm) - 1].manual_cost = rec.manual_cost
                sm[len(sm) - 1].manual_valuation = rec.quantity * rec.manual_cost
                svl = self.env['stock.valuation.layer'].search([('stock_move_id','=',sm[len(sm) - 1].id)])
                svl[0].unit_cost = rec.manual_cost
                svl[0].value = svl[0].quantity * svl[0].unit_cost """
            sml = self.env['stock.move.line'].search([('move_id','=',sm[len(sm) - 1].id)])
            for line in sml:
                line.date = rec.backdate