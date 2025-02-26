# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTax(models.AbstractModel):
    _name = 'report.odb_account_reports_pdf.report_tax'
    _description = 'Tax Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    def _sql_from_amls_one(self, analytic_account_ids):
        if len(analytic_account_ids) > 0:
            analytic_sql = '(account_move_line.analytic_account_id in {}) AND'.format(tuple(analytic_account_ids))
        else:
            analytic_sql = ''
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE """ + analytic_sql + """ %s GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self, analytic_account_ids):
        if len(analytic_account_ids) > 0:
            analytic_sql = '(account_move_line.analytic_account_id in {}) AND'.format(tuple(analytic_account_ids))
        else:
            analytic_sql = ''
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                FROM %s
                INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                WHERE """ + analytic_sql + """ %s GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        # compute the tax amount
        analytic_account_ids = [int(x) for x in options['account_analytic_ids']]
        if len(analytic_account_ids) == 1:
            analytic_account_ids.append(0)
        sql = self._sql_from_amls_one(analytic_account_ids)
        tables, where_clause, where_params = self.env['account.move.line']._query_get(
        )
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['tax'] = abs(result[1])

        # compute the net amount
        sql2 = self._sql_from_amls_two(analytic_account_ids)
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {
                        'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {'tax': 0, 'net': 0,
                                 'name': tax.name, 'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'], date_to=options['date_to'],
                          state=options['target_move'],
                          strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['tax']:
                groups[tax['type']].append(tax)
        return groups
