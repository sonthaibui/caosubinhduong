# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name + ' (%s%s)' % (str(record.product_qty), record.product_uom_id.name)))
        return result
