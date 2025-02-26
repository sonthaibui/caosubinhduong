# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    deposit_id = fields.Many2one(comodel_name='payment.order.deposit', string='Deposits', ondelete='set null')