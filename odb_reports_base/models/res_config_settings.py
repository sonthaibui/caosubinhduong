# -*- coding: utf-8 -*-
from odoo import fields, models


class RestConfigSettings(models.TransientModel):

    _inherit = ["res.config.settings"]

    df_style = fields.Many2one(related='company_id.df_style', readonly=False)
    pdf_watermark = fields.Binary(related='company_id.pdf_watermark', readonly=False)
    pdf_watermark_fname = fields.Char(related='company_id.pdf_watermark_fname', readonly=False)
    pdf_last_page = fields.Binary(related='company_id.pdf_last_page', readonly=False)
    pdf_last_page_fname = fields.Char(related='company_id.pdf_last_page_fname', readonly=False)


    def config_report(self):
        action = self.env.ref('odb_reports_base.reports_styles_action').read()[0]
        return action
