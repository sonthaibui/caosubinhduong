# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    percent = fields.Float(string="Percent",default=100,required=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name + ('-' + str(record.percent))+"%"))
        return result

