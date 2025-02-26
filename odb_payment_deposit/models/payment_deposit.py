# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PaymentOrderDeposit(models.Model):
    _name = "payment.order.deposit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Payment Order Deposit"
    _order = "name desc, id desc"

    
    active = fields.Boolean(string='Active', default=True)
    name = fields.Date(string="Date", default=fields.Date.context_today)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner",# related="sale_id.partner_invoice_id.commercial_partner_id",
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]", check_company=True)
    journal_id = fields.Many2one("account.journal", string="Journal", domain=[("type", "in", ("bank", "cash"))])
    currency_id = fields.Many2one("res.currency", string="Currency")
    amount_total = fields.Monetary(string="Amount Total", readonly=True, currency_field="currency_id")
    amount_advance = fields.Monetary("Down Payment", readonly=True, currency_field="currency_id")
    amount_remain = fields.Monetary("Balance", readonly=True, currency_field="currency_id")
    payment_ref = fields.Char("Ref.")
    payment_type = fields.Selection([("inbound", "Inbound"), ("outbound", "Outbound")], default="inbound")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', readonly=False, store=True, required=True)
    state = fields.Selection(selection=[('draft', 'New'), ('confirm', 'Validated'), ('approve', 'Approved'), ('cancel', 'Canceled')],
        string='State', default='draft')
#    payment_ids = fields.One2many(string='Payment', comodel_name='account.payment', inverse_name='deposit_id',)
    payment_id = fields.Many2one(string='Payment', comodel_name='account.payment', ondelete='restrict',)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    description = fields.Char(string='Description',)

    @api.constrains("amount_total")
    def _check_amount_total(self):
        if self.amount_advance <= 0:
            raise ValidationError(_("Amount total must be positive."))

    def _prepare_account_payment(self, deposit_id):
        return {
            "name": str(deposit_id.name),
            "amount": deposit_id.amount_advance,
            "payment_type": deposit_id.payment_type,
            "ref": deposit_id.description,
            "journal_id": deposit_id.journal_id.id,
            "currency_id": deposit_id.currency_id.id,
            "partner_id": deposit_id.partner_id.id,
            "payment_method_id": deposit_id.payment_method_id.id,
        }

    def action_confirm(self):
        for depo in self:
            depo.write({
                'state': 'confirm'
            })
            # Cần call tiếp action gửi mail thông báo có deposit cho người tạo, người đã chạy action và kế toán

    def action_approve(self):
        payment_obj = self.env["account.payment"]
        for deposit_id in self:
            # if self.env.user.company_id.create_invoice_by_approve_sale_order:
            #     # plan to automatic create invoice.
            #     # But default, odoo allow this action in case stock.ping in Delivery Orders is Done
            #     pass
            vals = self._prepare_account_payment(deposit_id)
            payment = payment_obj.sudo().create(vals)
            # payment.action_post()
            # Chờ kế toán xác nhận thông tin sẽ mở hàm tự động post
            # Khi tạo xong cần gửi mail thông báo kế toán đã nhận payment cho người tạo
            deposit_id.write({'state': 'approve', 'payment_id': payment.id})

    def action_cancel(self):
        for depo in self:
            depo.write({
                'state': 'cancel'
            })

    def set_to_draft(self):
        for depo in self:
            depo.write({
                'state': 'draft'
            })
