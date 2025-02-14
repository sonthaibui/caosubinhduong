import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    kanban_state = fields.Selection(selection='_new_options', default='ba')

    @api.model
    def _new_options(self):
        selection = [
            ('ba', 'BA'),
            ('coding','Coding'),
            ('waitgd','Wait: GD Finalize'),
            ('waitit','Wait: IT Solution'),
            ('waitfix','Wait: Fix'),
            ('waittest','Wait: Test'),
            ('waitcl','Wait: Clarify'),
            ('work','Work'),
            ('cancel','Cancel'),
        ]
        return selection

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    giamdoc_duyet = fields.Boolean('Giám Đốc Duyệt', store=True, copy=True, tracking=True)
    ketoan_duyet = fields.Boolean('Kế Toán Duyệt', store=True, copy=True, tracking=True)
    ketoan_trang = fields.Boolean('KT Trang', store=True, copy=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    ghi_chu = fields.Char('Ghi Chú', tracking=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Tổ', store=True, copy=True, tracking=True)

    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.depends('previous_statement_id', 'previous_statement_id.balance_end_real')
    def _compute_ending_balance(self):
        super()._compute_ending_balance()
        latest_statement = self.env['account.bank.statement'].search([('journal_id', '=', self[0].journal_id.id)], limit=1)
        for statement in self:
            if statement.journal_type == 'cash':
                if latest_statement.id and statement.id == latest_statement.id and not float_is_zero(statement.balance_end_real, precision_digits=statement.currency_id.decimal_places):
                    statement.balance_end_real = statement.balance_end_real or 0.0
                else:
                    total_entry_encoding = sum([line.amount for line in statement.line_ids])
                    statement.balance_end_real = statement.previous_statement_id.balance_end_real + total_entry_encoding

    @api.onchange('analytic_id')
    def _onchange_analytic_id(self):
        if self.analytic_id:
            if len(self.line_ids) > 0:
                for line in self.line_ids:
                        line.phantich_id = self.analytic_id.id
        else:
            if len(self.line_ids) > 0:
                for line in self.line_ids:
                        line.phantich_id = False
    
    @api.onchange('balance_end')
    def _onchange_balance_end(self):
        self.balance_end_real = self.balance_end
        asts = self.env['account.bank.statement']
        for st in asts:
            if st.id > self._origin.id:
                st.balance_end = st.balance_start + st.total_entry_encoding

    def copy(self):
        vals = super(AccountBankStatement, self).copy()
        vals.giamdoc_duyet = False
        vals.ketoan_duyet = False
        for line in vals.line_ids:
            line.ketoan_duyet = False
            line.giamdoc_duyet = False
        #raise UserError(_(vals.giamdoc_duyet))
        return vals

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    taikhoan_id = fields.Many2one('account.account', string='Tai Khoan', store=True)
    phantich_id = fields.Many2one('account.analytic.account', string='Tổ', store=True)
    giamdoc_duyet = fields.Boolean('GĐ Duyệt', store=True, copy=True)
    ketoan_duyet = fields.Boolean('KT Duyệt', store=True, copy=True)
    ketoan_trang = fields.Boolean('KT Trang', store=True, copy=True)
    nguoitao = fields.Char(related='statement_id.nguoitao')
    ghi_chu = fields.Char('Ghi Chú', store=True, copy=True)
    #bill_id = fields.Many2one('account.move', string='Bill')#, domain=['|',('payment_state','=','not_paid'),('payment_state','=','partial')])

    """ @api.onchange('bill_id')
    def _onchange_bill_id(self):
        for rec in self:
            if rec.partner_id:
                return {'domain': {'bill_id': [('invoice_partner_display_name', '=', rec.partner_id.name),'|',('payment_state','=','not_paid'),('payment_state','=','partial')]}}
 """
    @api.model
    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        [liquidity_line_vals, counterpart_line_vals] = super()._prepare_move_line_default_vals()
        if self.taikhoan_id:
            counterpart_account_id = self.taikhoan_id.id
            counterpart_line_vals.update({'account_id': counterpart_account_id})
        if self.phantich_id:
            counterpart_line_vals['analytic_account_id'] = self.phantich_id.id
        return [liquidity_line_vals, counterpart_line_vals]
    
    @api.onchange('taikhoan_id', 'phantich_id')
    def _onchange_taikhoan_id(self):
        if self.payment_ref:
            label = self.payment_ref
            lastchar = label[-1]
            if lastchar == '.':
                self.payment_ref = label[:-1]
            else:
                self.payment_ref = label + '.'

    @api.onchange('ghi_chu')
    def _onchange_ghi_chu(self):
        if self.ghi_chu:
            statement_id = self.env['account.bank.statement'].search([('journal_id','=',self.statement_id.journal_id.id)])
            notification_ids = []
            notification_ids.append((0, 0, {
                'res_partner_id': self.env['res.users'].browse(41).partner_id.id,
                'notification_type': 'inbox'
            }))
            self.env['mail.message'].create(
                {
                    'message_type': 'notification',
                    'body': self.payment_ref + ': ' + self.ghi_chu,
                    'subject': statement_id[0].name + statement_id[0].journal_id.name,
                    'partner_ids': [(4, self.env['res.users'].browse(41).partner_id.id)],
                    'model': self._name,
                    'subtype_id': self.env.ref("mail.mt_comment").id,
                    'res_id': self.id,
                    'author_id': self.env.user.partner_id and self.env.user.partner_id.id,
                    'notification_ids': notification_ids,
                }
            )

    @api.model
    def create(self, vals):
        res = super(AccountBankStatementLine, self).create(vals)
        if res.statement_id.analytic_id:
            res.phantich_id = res.statement_id.analytic_id.id
        return res
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ngay = fields.Integer('Ngay', compute='_compute_ntq', store=True, copy=True)
    thang = fields.Char('Thang', compute='_compute_ntq', store=True, copy=True)
    quy = fields.Char('Quy', compute='_compute_ntq', store=True, copy=True)
    stock_move_id = fields.Many2one('stock.move', related='move_id.stock_move_id', string='Stock Move')
    giamdoc_duyet = fields.Boolean('GĐ Duyệt', store=True, copy=True)
    ketoan_duyet = fields.Boolean('KT Duyệt', store=True, copy=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)
        
    @api.depends('date')
    def _compute_ntq(self):
        for rec in self:
            if rec.date:
                rec.ngay = rec.date.timetuple().tm_yday
                thang = rec.date.month
                if thang < 10:
                    rec.thang = "Tháng 0" + str(thang)
                else:
                    rec.thang = "Tháng " + str(thang)
                rec.quy = "Quý " + str(math.ceil(rec.date.month / 3))

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

class AccountMove(models.Model):
    _inherit = "account.move"

    giamdoc_duyet = fields.Boolean('Giám Đốc Duyệt', store=True, copy=True, tracking=True)
    ketoan_duyet = fields.Boolean('Kế Toán Duyệt', store=True, copy=True, tracking=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.invoice_has_outstanding == True:
            aml = self.env['account.move.line'].search([('move_id','=',self.id)])
            for am in aml:
                if not am.analytic_account_id:
                    am.analytic_account_id = aml[0].analytic_account_id
        return True
    
    def copy(self):
        vals = super(AccountMove, self).copy()
        vals.giamdoc_duyet = False
        vals.ketoan_duyet = False
        for line in vals.line_ids:
            line.x_ketoan_duyet = False
        #line.giamdoc_duyet = False
        #raise UserError(_(vals.giamdoc_duyet))
        return vals

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

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sanluong = fields.Float(string='Sản Lượng')
    do = fields.Float(string='Độ')

    @api.onchange('sanluong', 'do')
    def onchange_sanluong_do(self):
        self.product_qty = self.sanluong * (self.do / 100)