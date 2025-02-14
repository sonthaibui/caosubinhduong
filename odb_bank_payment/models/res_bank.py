# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Bank(models.Model):
    _inherit = "res.bank"

    payment_icon_id = fields.Many2one(string='Payment Icon', comodel_name='payment.icon', ondelete='restrict',)
    image_icon = fields.Image(string="Image displayed on the payment form", related='payment_icon_id.image',
        store=True, max_width=64, max_height=64)
