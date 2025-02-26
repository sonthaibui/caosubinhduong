# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import date


class AccountTaxReport(models.TransientModel):
    _name = 'account.tax.report.wizard'
    _inherit = "account.common.report"
    _description = 'Tax Report'

    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: fields.Date.to_string(date.today()))
    account_analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        string='Account Analytic'
    )

    def check_report(self):
        res = super(AccountTaxReport, self).check_report()
        res['data']['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id', 'account_analytic_ids'])[0]
        return res

    def _print_report(self, data):
        return self.env.ref('odb_account_reports_pdf.action_report_account_tax').report_action(self, data=data)
