# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    style = fields.Many2one(
        'report.template.settings',
        'Reports Style',
        help="Select a style to use when printing reports for this customer",
        default=lambda self: self.env.user.company_id.df_style)
