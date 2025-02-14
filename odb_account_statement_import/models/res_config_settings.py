# -*- coding: utf-8 -*-
import odoo
import base64
from odoo import models, api, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    sample_import_csv_name = fields.Char(default='import_statement_account.csv')
    sample_import_excel_name = fields.Char(default='import_statement_account.xlsx')
    file_name = fields.Char('File', size=64)

    # sample_import_csv = fields.Binary(default='_default_sample_import_csv')
    # sample_import_excel = fields.Binary(default='_default_sample_sheet_excel')

    # def _default_sample_import_csv(self):
    #     csv_path = odoo.modules.module.get_resource_path(
    #         'odb_account_statement_import', 'sample_files', 'import_statement_account.csv')
    #     with open(csv_path, 'rb') as imp_sheet:
    #         sample_file = imp_sheet.read()
    #     return sample_file and base64.b64encode(sample_file)

    # def get_sample_import_csv(self):
    #     module = __name__.split("addons.")[1].split(".")[0]
    #     url = "web/%s/download/import_statement_account.xlsx" % module
    #     return {
    #         'name': 'Bank Statement Sample CSV',
    #         'type': 'ir.actions.act_url',
    #         'url': ("web/content/?model=" + self._name + "&id=" +
    #                 str(self.id) + "&filename_field=sample_import_sheet_name&"
    #                                "field=sample_import_sheet&download=true&"
    #                                "filename=import_statement_account.csv"),
    #         'target': 'self',
    #     }

    def get_sample_import_csv(self):
        module = __name__.split("addons.")[1].split(".")[0]
        url = "%s/static/download/import_statement_account.csv" % module
        return {
            'name': 'Bank Statement Sample CSV',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    def get_sample_import_excel(self):
        module = __name__.split("addons.")[1].split(".")[0]
        url = "%s/static/download/import_statement_account.xlsx" % module
        return {
            'name': 'Bank Statement Sample EXCEL',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
