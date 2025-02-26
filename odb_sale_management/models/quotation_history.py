# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderRevised(models.Model):
    _name = 'quotation.history'
    _rec_name = 'revised_number'
    _description = 'Sale Order Revised'

    sale_order_id = fields.Many2one('sale.order', string='Sale order',)
    revised_number = fields.Char(string='Revision Number', readonly=True,)
    revised_line_ids = fields.One2many(
        'quotation.history.line',
        'line_custom_id',
        string='Revision Sales Line',
        readonly=True,
    )
    sale_person_id = fields.Many2one(
        'res.users',
        string='Sales Person',
        related='sale_order_id.user_id',
        store=True,
    )
