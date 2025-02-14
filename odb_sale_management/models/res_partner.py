from odoo import fields, models, api

class SaleContact(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string='Is Customer')

    @api.model
    def create(self, vals):
        if vals.get("is_customer") == True or self._context.get('res_partner_search_mode') == 'customer':
            vals.update({
                'barcode':self.env['ir.sequence'].next_by_code('sale.contact'),
                'is_customer':True
            })
        return super(SaleContact, self).create(vals)

