import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class StockMove(models.Model):
    _inherit = "stock.move"

    valuation = fields.Float(compute='_compute_valuation', string='Valuation')
    #manual_cost = fields.Float('Manual Cost')
    #manual_valuation = fields.Float('Manual Valuation')

    def _compute_valuation(self):
        for rec in self:
            value = 0
            for line in rec.move_line_ids:
                if line.valuation:
                    value += line.valuation
            rec.valuation = value
    
    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        vals = super(StockMove, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
        sche = self.picking_id.scheduled_date
        ana = 'account.analytic.account'
        aid = 'analytic_account_id'
        if self.picking_id.purchase_id:
            if sche.date() < datetime.date.today():
                self.date = sche
                self.picking_id.date_done = sche
                sml = self.env['stock.move.line'].search([('move_id','=',self.id)])
                for line in sml:
                    line.date = sche
                vals['date'] = sche
        if self.picking_id.sale_id:
            sml = self.env['stock.move.line'].search([('move_id','=',self.id)])
            if self.env[ana].search([('name','=',sml.location_id.name)]):
                if sche.date() < datetime.date.today():
                    self.date = sche
                    self.picking_id.date_done = sche
                    self.env['stock.move.line'].search([('move_id','=',self.id)]).date = sche
                    vals['date'] = sche
                vals['line_ids'][0][2][aid] = self.env[ana].search([('name','=',sml.location_id.name)]).id
                vals['line_ids'][1][2][aid] = self.env[ana].search([('name','=',sml.location_id.name)]).id
        if self.picking_id.picking_type_id.name == "Internal Transfers" and self.picking_id.picking_type_id.warehouse_id.name == "KONTUM":
            src = self.picking_id.location_id.name
            dest = self.picking_id.location_dest_id.name
            if src != dest:
                if src[:2] == 'Tổ' and dest[:4] == 'Vườn' and src != dest[5:]:
                    raise UserError(_("Stock location to virtual location must same department."))
                if src[:4] == 'Vườn' and dest[:4] == 'Vườn':
                    raise UserError(_("Virtual location can not move to virtual location."))
                if sche.date() < datetime.date.today():
                    self.date = sche
                    self.picking_id.date_done = sche
                    self.env['stock.move.line'].search([('move_id','=',self.id)]).date = sche
                    vals['date'] = sche
                if src[:4] == 'Vườn' and dest[:2] == 'Tổ':
                    prd = self.env['product.product'].search([('id', '=', vals['line_ids'][0][2]['product_id'])])
                    vals['line_ids'][0][2][aid] = self.env[ana].search([('name','=',src[5:])]).id
                    vals['line_ids'][0][2]['account_id'] = prd.categ_id.property_stock_account_output_categ_id.id
                    vals['line_ids'][1][2][aid] = self.env[ana].search([('name','=',dest)]).id
                elif src[:2] == 'Tổ' and dest[:4] == 'Vườn' and src == dest[5:]:
                    vals['line_ids'][0][2][aid] = self.env[ana].search([('name','=',src)]).id
                    vals['line_ids'][1][2][aid] = self.env[ana].search([('name','=',dest[5:])]).id
                #if src in dest:
                #raise UserError(_(src + ' - ' + dest))
                """ if self.env[ana].search([('name','=',src)]):
                    if not self.env[ana].search([('name','=',dest)]):
                        if sche.date() < datetime.date.today():
                            self.date = sche
                            self.picking_id.date_done = sche
                            self.env['stock.move.line'].search([('move_id','=',self.id)]).date = sche
                            vals['date'] = sche
                        vals['line_ids'][0][2][aid] = self.env[ana].search([('name','=',src)]).id
                        vals['line_ids'][1][2][aid] = self.env[ana].search([('name','=',src)]).id
                if self.env[ana].search([('name','=',dest)]):
                    if not self.env[ana].search([('name','=',src)]):
                        if sche.date() < datetime.date.today():
                            self.date = sche
                            self.picking_id.date_done = sche
                            vals['date'] = sche
                            self.env['stock.move.line'].search([('move_id','=',self.id)]).date = sche
                        vals['line_ids'][0][2][aid] = self.env[ana].search([('name','=',dest)]).id
                        vals['line_ids'][1][2][aid] = self.env[ana].search([('name','=',dest)]).id """
            else:
                raise UserError(_('Source location and destination cannot be same.'))
        return vals
    
    def _create_internal_journals(self):
        src = self.picking_id.location_id.name
        dest = self.picking_id.location_dest_id.name
        sche = self.picking_id.scheduled_date
        ana = 'account.analytic.account'
        st = self.picking_id.name
        pr = self.product_id.name
        ct = self.picking_id.partner_id
        if src != dest:
            if src[:2] == 'Tổ' and dest[:2] == 'Tổ':
                if sche.date() < datetime.date.today():
                    self.date = sche
                    self.picking_id.date_done = sche
                    self.env['stock.move.line'].search([('move_id','=',self.id)]).date = sche
                am_vals = {
                    'date': sche if sche.date() < datetime.date.today() else self._context.get('force_period_date', fields.Date.context_today(self)),
                    'journal_id': self.env['account.journal'].search([('name','=','Inventory Valuation')]).id,
                    'company_id': self.company_id.id,
                    'move_type': 'entry',
                    'stock_move_id': self.id,
                    'state': 'draft',
                    'ref': st + ' - ' + pr,
                }
                account_moves = self.env['account.move'].sudo().create(am_vals)
                for line in self.move_line_ids:
                    move_lines = []
                    credit_vals = {
                        'name': st + ' - ' + pr + ': From ' + src + ' to ' + dest,
                        'quantity': line.qty_done,
                        'partner_id': (ct and self.env['res.partner']._find_accounting_partner(ct).id) or False,
                        'account_id': self.env['account.account'].search([('code','=','1561')]).id,
                        'debit': 0,
                        'credit': line.product_id.standard_price * line.qty_done,
                        'product_uom_id': line.product_id.uom_id.id,
                        'ref': st,
                        'move_id': account_moves.id,
                        'product_id': line.product_id.id,
                        'company_id': line.company_id.id,
                        'analytic_account_id': self.env['account.analytic.account'].search([('name','=',self.picking_id.location_id.name)]).id,
                    }
                    move_lines.append((0, 0, credit_vals))
                    debit_vals = {
                        'name': st + ' - ' + pr + ': From ' + src + ' to ' + dest,
                        'quantity': line.qty_done,
                        'partner_id': (ct and self.env['res.partner']._find_accounting_partner(ct).id) or False,
                        'account_id': self.env['account.account'].search([('code','=','1561')]).id,
                        'debit': line.product_id.standard_price * line.qty_done,
                        'credit': 0,
                        'product_uom_id': line.product_id.uom_id.id,
                        'ref': st,
                        'move_id': account_moves.id,
                        'product_id': line.product_id.id,
                        'company_id': line.company_id.id,
                        'analytic_account_id': self.env['account.analytic.account'].search([('name','=',self.picking_id.location_dest_id.name)]).id,
                    }
                    move_lines.append((0, 0, debit_vals))
                    """ svl_vals_list = []
                    svl_vals = line.product_id._prepare_in_svl_vals(line.qty_done, line.product_id.standard_price)
                    svl_vals.update(self._prepare_common_svl_vals())
                    svl_vals_list.append(svl_vals)
                    self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
                account_moves.write({'stock_valuation_layer_ids': [(6, None, [self.env['stock.valuation.layer'].search([('stock_move_id','=',self.id)]).id])]}) """
                account_moves.write({'line_ids': move_lines})
                account_moves._post()
        else:
            raise UserError(_('Source location and destination location can not be same!'))
        return True