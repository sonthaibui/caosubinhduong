# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WizardSplitSaleOrder(models.TransientModel):
    _name = "wizard.split.sale.order.line"
    _description = "Wizard Split Sale Order Line"

    wz_sale_id = fields.Many2one(comodel_name='wizard.split.sale.order')
    so_line_id = fields.Many2one('sale.order.line', string='Sale Line')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    commitment_date = fields.Date(string='Commitment Date', )
    description = fields.Char(string='Description')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
    partner_id = fields.Many2one('res.partner', string='Customer',)
    selected_field = fields.Boolean(string='Select', default=False)