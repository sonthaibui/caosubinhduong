# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class SaleTemplateSettings(models.Model):
    _inherit = "report.template.settings"

    def _get_default_so_template(self):
        return self.env['ir.ui.view'].search([('key', '=', 'odb_sale_management.SO_0_document'), ('type', '=', 'qweb')], order='key asc', limit=1)

    template_so = fields.Many2one(string='Order/Quote Template', comodel_name='ir.ui.view', default=_get_default_so_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'odb_sale_management.SO\_%\_document')]")