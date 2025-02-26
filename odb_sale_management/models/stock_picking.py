# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    commitment_date = fields.Date(string='Delivery Date')
