# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PaymentOrderDeposit(models.Model):
    _inherit = "payment.order.deposit"

    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale Order', ondelete='set null')

    def _prepare_account_payment(self, deposit_id):
        vals = super(PaymentOrderDeposit, self)._prepare_account_payment(deposit_id)
        if deposit_id.sale_id:
            vals.update({
                "sale_id": deposit_id.sale_id.id,
                "name": ('%s: %s' % (str(deposit_id.name), deposit_id.sale_id.name)),
            })
        return vals

    def action_confirm(self):
        template_id = self.env.ref('odb_payment_deposit_sale.deposit_confirm_mail')
        subject = 'DEPOSIT CONFIMRED : %s' % (self.name)
        email_values = {
            'email_to': self.env.user.email,
            'email_cc': self.create_uid.email,
            'subject': subject,
        }
        for depo in self:
            if depo.sale_id:
                template_id.send_mail(self.id, email_values=email_values)
                return super(PaymentOrderDeposit, self).action_confirm()

    def action_approve(self):
        template_id = self.env.ref('odb_payment_deposit_sale.deposit_confirm_mail')
        subject = 'DEPOSIT APPROVE : %s' % (self.name)
        email_values = {
            'email_to': self.env.user.email,
            'email_cc': self.create_uid.email,
            'subject': subject,
        }
        for depo in self:
            if depo.sale_id:
                template_id.send_mail(self.id, email_values=email_values)
                return super(PaymentOrderDeposit, self).action_approve()