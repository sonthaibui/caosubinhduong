# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    image_icon = fields.Image(
        string="Image displayed on the payment form", related='bank_id.image_icon', store=True, max_width=64,
        max_height=64)