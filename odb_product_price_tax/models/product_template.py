#coding: utf-8
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    list_price_tax = fields.Float(string="Sale Price (TAX)", tracking=True,)

    def action_list_price_tax(self):
        for tmpl_id in self:
            if tmpl_id.list_price_tax > 0:
                tmpl_id.compute_list_price_tax()

    def compute_list_price_tax(self):
        if self.list_price_tax > 0:
            tax_id = self.taxes_id[0]
            if tax_id.amount_type == 'percent':
                self.list_price = self.list_price_tax / \
                    ((tax_id.amount + 100)/100)
            else:
                self.list_price = self.list_price_tax
