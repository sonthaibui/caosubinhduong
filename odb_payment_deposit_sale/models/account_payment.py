# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale Order', ondelete='set null')