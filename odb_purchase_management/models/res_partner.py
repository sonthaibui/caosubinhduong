# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit='res.partner'

    is_vendor = fields.Boolean(string='Is Vendor')

    @api.model
    def create(self, vals):
        if vals.get("is_vendor") == True or self._context.get('res_partner_search_mode') == 'supplier':
            vals.update({
                'barcode':self.env['ir.sequence'].next_by_code('supplier.sequence'),
                'is_vendor':True
            })
        return super(ResPartner, self).create(vals)

