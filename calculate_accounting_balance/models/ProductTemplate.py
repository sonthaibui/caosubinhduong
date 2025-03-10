from odoo import api, fields, models, _
class ProductTemplate(models.Model):
    _inherit = "product.template"

    abbre = fields.Char(string = 'Viết tắt')
    kg_bao = fields.Float(string = 'Kg/bao', digits=(16, 0))
    N = fields.Float(string = 'N', digits=(16, 2))
    P = fields.Float(string = 'P2O5', digits=(16, 2))
    K = fields.Float(string = 'K2O', digits=(16, 2))
    Mg = fields.Float(string = 'MgO', digits=(16, 2))
    Ca = fields.Float(string = 'CaO', digits=(16, 2))
    Si = fields.Float(string = 'SiO2', digits=(16, 2))
    OM = fields.Float(string = 'OM', digits=(16, 2))
    Humic = fields.Float(string = 'Humic', digits=(16, 2))
    color = fields.Char(string='Color', default='#875A7B')