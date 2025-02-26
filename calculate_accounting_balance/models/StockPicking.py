import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockPicking(models.Model):
    _inherit = "stock.picking"

    analytic_id = fields.Many2one('account.analytic.account', string='Tổ')

    @api.onchange('analytic_id')
    def _onchange_analytic_id(self):
        if self.analytic_id:
            if str(self.id).replace('NewId_', '')[0:2] == "0x":
                print(str(self.id).replace('NewId_', '')[0:2])
            else:
                picking = int(str(self.id).replace('NewId_', ''))
                if self.env['stock.move'].search([('picking_id','=',picking)]):
                    sms = self.env['stock.move'].search([('picking_id','=',picking)])
                    for sm in sms:
                        if self.env['account.move'].search([('stock_move_id','=',sm.id)]):
                            am = self.env['account.move'].search([('stock_move_id','=',sm.id)])
                            aml = self.env['account.move.line'].search([('move_id','=',am.id)])
                            #if aml[0].analytic_account_id != None:
                                #aml[0].analytic_account_id = None
                            aml[0].analytic_account_id = self.analytic_id
                            aml[1].analytic_account_id = self.analytic_id
                self.update({'analytic_id': self.analytic_id})

    def copy(self):
        vals = super(StockPicking, self).copy()
        if self.purchase_id:
            if self.env['stock.move'].search([('picking_id','=',vals.id)]):
                sm = self.env['stock.move'].search([('picking_id','=',vals.id)])
                smc = self.env['stock.move'].search([('picking_id','=',self.id)])
                for x in range(len(sm)):
                    if self.env['stock.move.line'].search([('move_id','=',smc[x].id)]):
                        smlc = self.env['stock.move.line'].search([('move_id','=',smc[x].id)])
                        for y in range(len(smlc)):
                            smlc[y].copy().move_id = sm[x].id
                        sm[x]._action_confirm()
                        vals.update({'note':''})
                        sm[x]._set_quantities_to_reservation()
                        sml = self.env['stock.move.line'].search([('move_id','=',sm[x].id)])
                        sml[0].qty_done = 0
                        for z in range(len(smlc)):
                            sml[z + 1].location_dest_id = smlc[z].location_dest_id.id
                            sml[z + 1].qty_done = smlc[z].qty_done
        return vals

    def button_validate(self):
        super(StockPicking, self).button_validate()
        """ if self.purchase_id:
            sm = self.env['stock.move'].search([('origin','=',self.purchase_id.name)])
            #sm = self.env['stock.move'].search([('picking_id','=',self.id)])
            #self.scheduled_date = sm[0].date
            for l in sm:
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
                    am.action_post() """
        if self.purchase_id or self.sale_id:
            for line in self.move_line_ids_without_package:
                if line.product_id.detailed_type == "consu":
                    raise UserError(_("Consumable products can not transfer."))
        if self.picking_type_id.name == "Internal Transfers" and self.picking_type_id.warehouse_id.name == "KONTUM":
            #self.date_done = self.scheduled_date
            for line in self.move_lines:
                if line.product_id.detailed_type == "consu":
                    raise UserError(_("Consumable products can not transfer."))
                line._create_internal_journals()
                #line.date = self.scheduled_date
                #self.env['stock.move.line'].search([('move_id','=',line.id)]).date = self.scheduled_date
        return True
    
    def action_cancel(self):
        src = self.location_id.name
        dest = self.location_dest_id.name
        quant_obj= self.env['stock.quant']
        if self.picking_type_id.name == "Internal Transfers" and self.picking_type_id.warehouse_id.name == "KONTUM" and (dest[:2] == 'Tổ' and src[:4] == 'Vườn') or (dest[:4] == 'Vườn' and src[:2] == 'Tổ'):
            for line in self.move_ids_without_package:
                if line.state == "done":
                    account_moves = self.env['account.move'].search([('stock_move_id', '=', line.id)])
                    valuation = line.stock_valuation_layer_ids
                    valuation and valuation.sudo().unlink()
                    if account_moves:
                        for account_move in account_moves:
                            account_move.button_cancel()
                            account_move.sudo().unlink()
            for line in self.move_line_ids_without_package:
                if line.state == "done":
                    if line.product_id.detailed_type != "consu":
                        quantity = line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_id, quantity,line.lot_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_dest_id, quantity * -1,line.lot_id)
        elif self.picking_type_id.name == "Internal Transfers" and self.picking_type_id.warehouse_id.name == "KONTUM" and (dest[:2] == 'Tổ' and src[:2] == 'Tổ'):
            for line in self.move_lines:
                if line.state == 'done':
                    account_moves = self.env['account.move'].search([('stock_move_id', '=', line.id)])
                    #valuation = line.stock_valuation_layer_ids
                    #valuation and valuation.sudo().unlink()
                    if account_moves:
                        for account_move in account_moves:
                            account_move.button_cancel()
                            account_move.sudo().unlink()
            for line in self.move_line_ids:
                if line.state == 'done':
                    if line.product_id.detailed_type != "consu":
                        quantity = line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_id, quantity,line.lot_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_dest_id, quantity * -1,line.lot_id)
        if self.purchase_id or self.sale_id:
            for line in self.move_ids_without_package:
                if line.state == 'done':
                    account_moves = self.env['account.move'].search([('stock_move_id', '=', line.id)])
                    valuation = line.stock_valuation_layer_ids
                    #raise UserError(_(valuation.display_name))
                    valuation and valuation.sudo().unlink()
                    if account_moves:
                        for account_move in account_moves:
                            account_move.button_cancel()
                            account_move.sudo().unlink()
            for line in self.move_line_ids_without_package:
                if line.state == 'done':
                    if line.product_id.detailed_type != "consu":
                        quantity = line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_id, quantity,line.lot_id)
                        quant_obj._update_available_quantity(line.product_id, line.location_dest_id, quantity * -1,line.lot_id)
        super(StockPicking, self).action_cancel()
        return True