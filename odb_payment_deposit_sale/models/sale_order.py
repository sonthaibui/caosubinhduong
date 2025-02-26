# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_payment_ids = fields.One2many('account.payment', 'sale_id', string='Account Payments')
    payment_deposit_ids = fields.One2many('payment.order.deposit', 'sale_id', string='Deposits')
    deposit_amount = fields.Float('Deposit amount', readonly=True, compute='_compute_advanced_payment', store=True,)
    deposit_remain = fields.Float('Amount Remain', readonly=True, compute='_compute_advanced_payment', store=True,)
    payment_line_ids = fields.Many2many('account.move.line', string='Payment move lines', compute='_compute_advanced_payment', store=True,)
    advance_payment_status = fields.Selection(selection=[('not_paid', 'Not Paid'), ('paid', 'Paid'), ('partial', 'Partially Paid')],
        string='Payment Status', store=True, readonly=True, copy=False, tracking=True, compute='_compute_advanced_payment')

    @api.depends('currency_id', 'company_id', 'amount_total', 'payment_deposit_ids', 'invoice_ids.amount_residual')
    def _compute_advanced_payment(self):
        for order in self:
            deposit_amount = sum(order.payment_deposit_ids.mapped('amount_advance'))
            payment_status = 'not_paid'
            # Consider payments in related invoices.
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_paid_amount += inv.amount_total - inv.amount_residual
            deposit_remain = order.amount_total - (deposit_amount + invoice_paid_amount)
            
            if deposit_amount > 0.0:
                payment_status = 'paid'
                has_due_amount = float_compare(deposit_remain, 0.0, precision_rounding=order.currency_id.rounding)
                if has_due_amount > 0:
                    payment_status = 'partial'

            order.write({
                'deposit_remain': deposit_remain,
                'deposit_amount': deposit_amount,
                'advance_payment_status': payment_status,
            })

    def add_payment_deposit(self):
        self.ensure_one()
        wz_form = self.env.ref('odb_payment_deposit_sale.sale_payment_deposit_wizard_form_view_inherit')
        journal_domain = [('company_id', '=', self.env.company.id), ('type', '=', 'bank')]
        journal_id = self.env['account.journal'].search(journal_domain, limit=1)
        return {
            'name': 'Add Payment Deposit',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.order.deposit.wizard',
            'views': [(wz_form.id, 'form')],
            'view_id': wz_form.id,
            'target': 'new',
            'context': {
                'default_sale_id': self.id,
                'default_payment_ref': self.name,
                'default_amount_total': self.deposit_amount,
                'default_currency_id': self.currency_id.id,
                'default_journal_currency_id': self.currency_id.id,
                'default_journal_id': journal_id.id if journal_id else False,
                'default_payment_type': 'inbound',
            },
        }

    def _create_sale_order_deposit(self):
        payment_deposit_obj = self.env["payment.order.deposit"]
        journal_id = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        for sale in self:
            pay_term_ids = self.payment_term_id.line_ids.filtered(lambda x: x.option == 'day_after_invoice_date' and x.days == 0)
            if pay_term_ids and sale.deposit_amount == 0.0 and sale.amount_total > 0.0:
                deposit_amount = 0.0
                for term_id in pay_term_ids:
                    if term_id.value == 'balance':
                        continue
                    elif term_id.value == 'percent':
                        deposit_amount += (term_id.value_amount / 100.0) * sale.amount_total
                    else: # fixed.
                        deposit_amount += term_id.value_amount
                payment_deposit_obj.create({
                    'sale_id': sale.id,
                    'payment_ref': sale.name,
                    'amount_total': deposit_amount,
                    'name': fields.Date.today(),
                    'currency_id': sale.currency_id.id,
                    'journal_id': journal_id.id if journal_id else False,
                    'partner_id': sale.partner_invoice_id.commercial_partner_id.id,
                    'payment_method_id': self.env.ref("account.account_payment_method_manual_in").id,
                })

    # def action_request(self):
    #     super(SaleOrder, self).action_request()
    #     self._create_sale_order_deposit()

    # def action_approve(self):
    #     super(SaleOrder, self).action_approve()
    #     payment_obj = self.env["account.payment"]
    #     for sale_id in self:
    #         if self.env.user.company_id.create_invoice_by_approve_sale_order:
    #             pass # plan to automatic create invoice.
    #             # But default, odoo allow this action in case stock.ping in Delivery Orders is Done
    #         # create account.payment
    #         for deposit_id in sale_id.payment_deposit_ids:
    #             payment = payment_obj.sudo().create({
    #                 "sale_id": deposit_id.sale_id.id,
    #                 "name": deposit_id.date,
    #                 "amount": deposit_id.amount_total,
    #                 "payment_type": deposit_id.payment_type,
    #                 "ref": deposit_id.payment_ref,
    #                 "journal_id": deposit_id.journal_id.id,
    #                 "currency_id": deposit_id.currency_id.id,
    #                 "partner_id": deposit_id.partner_id.id,
    #                 "payment_method_id": deposit_id.payment_method_id.id,
    #             })
    #             payment.action_post()
