import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def _validate_accounting_entries(self):
        super(StockValuationLayer, self)._validate_accounting_entries()
        for svl in self:
            if svl.stock_move_id.picking_id.purchase_id:
                l = svl.stock_move_id
                sml = self.env['stock.move.line'].search([('move_id','=',l.id)])
                if self.env['account.move'].search([('stock_move_id','=',l.id)]):
                    am = self.env['account.move'].search([('stock_move_id','=',l.id)])
                    ams = self.env['account.move.line'].search([('move_id','=',am.id)])
                    for al in sml:
                        aml = ams[1].sudo().with_context(check_move_validity=False).copy()
                        aml.debit = al.qty_done * ams[1].debit / l.quantity_done
                        aml.balance = aml.debit
                        if self.env['account.analytic.account'].search([('name','=',al.location_dest_id.name)]):
                            aml.analytic_account_id = self.env['account.analytic.account'].search([('name','=',al.location_dest_id.name)]).id
                    am.button_draft()
                    ams[1].sudo().with_context(check_move_validity=False).unlink()
                    am.action_post()
            #raise UserError(_(svl.stock_move_id))