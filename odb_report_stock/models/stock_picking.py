from odoo import _, api, fields, models

class Picking(models.Model):
    _inherit = "stock.picking"

    def _default_so_style(self):
        return self.env.user.company_id.df_style

    style = fields.Many2one('report.template.settings', 'Stock Picking Style', default= _default_so_style,
        help="Select Style to use when printing the Stock Picking")