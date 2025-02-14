# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountPrintJournal(models.TransientModel):
    _name = "account.print.journal"
    _inherit = "account.common.journal.report"
    _description = "Account Print Journal"

    sort_selection = fields.Selection([('date', 'Date'), ('move_name', 'Journal Entry Number')],
                                      'Entries Sorted by', required=True, default='move_name')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search([('type', 'in', ['sale', 'purchase'])]))
    account_analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        string='Account Analytic',
    )

    def check_report(self):
        res = super(AccountPrintJournal, self).check_report()
        res['data']['form']['account_analytic_ids'] = self.read(['account_analytic_ids'])[0]['account_analytic_ids']
        return res

    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'sort_selection': self.sort_selection})
        return data

    def _print_report(self, data):
        data = self._get_report_data(data)
        return self.env.ref('odb_account_reports_pdf.action_report_journal').with_context(landscape=True).report_action(self, data=data)
