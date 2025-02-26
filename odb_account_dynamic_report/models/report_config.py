# -*- coding: utf-8 -*-
import io
import time
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class DynamicReportConfig(models.TransientModel):
    _name = 'dynamic.report.config'

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': '12px', 'bold': True})

        txt = workbook.add_format({'font_size': '10px'})

        x = 0
        y = 0

        if data['filters']:
            filters = data['filters']
            if filters.get('date_from'):
                sheet.merge_range(y, x, y, x + 2, filters['date_from'],
                                  cell_format)
                x += 2
            if filters.get('date_to'):
                sheet.merge_range(y, x, y, x + 2, filters['date_to'],
                                  cell_format)

            x = 0
            if filters.get('date_from') or filters.get('date_to'):
                y += 1

            if filters.get('journal_ids'):
                sheet.merge_range(y, x, y, x + 4, filters['journal_ids'],
                                  cell_format)
                y += 1
            x = 0

            for f_val in filters:
                if f_val in ['date_from',
                             'date_to', 'journal_ids'] or not filters[f_val]:
                    continue
                sheet.merge_range(y, x, y, x + 2, filters[f_val],
                                  cell_format)
                y += 1

        y += 1
        col_style = cell_format
        col_width = {}
        new_vals = []
        for line in data.get('lines'):
            temp = {}
            for l_col in line:
                temp[int(l_col)] = line[l_col]
            new_vals.append(temp)

        for line in new_vals:
            x = 0
            for col in line:
                col_val = str(line[col]['value'])
                colspan = 0
                if line[col].get('colspan'):
                    colspan = int(line[col]['colspan'])

                col_level = 0
                if line[col].get('level'):
                    col_level = int(line[col]['level'])
                new_col_style = None
                if x == 0 and col_level > 0:
                    new_col_style = workbook.add_format({
                        'font_size': '10px'})

                    if data['report_name'] not in ['journals_audit',
                                                   'aged_partner',
                                                   'trial_balance',
                                                   'partner_ledger',
                                                   'general_ledger',
                                                   'tax_report']:
                        col_level = math.ceil(col_level / 2)
                    new_col_style.set_indent(col_level)

                if not new_col_style:
                    new_col_style = col_style

                sheet.write(y, x, col_val, new_col_style)

                x += colspan

                if col in col_width:
                    if col_width[col] < colspan:
                        col_width[col] = colspan
                else:
                    col_width[col] = 1

            col_style = txt
            sheet.set_row(y, 25)
            y += 1

        if data['report_name'] in ['journals_audit', 'aged_partner',
                                   'partner_ledger', 'general_ledger',
                                   'tax_report']:
            min_col_width = 15
        else:
            min_col_width = 30

        for col in col_width:
            width_val = col_width[col] * min_col_width
            if width_val > min_col_width:
                width_val = min_col_width
            sheet.set_column(int(col), int(col), width_val)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def prepare_data(self):
        now = datetime.now()
        format_my = '%s %s'%(datetime.strptime(str(now.month), "%m").strftime("%b"), now.year)
        date_from = '%s'%(now.replace(day=1).date())
        date_to = '%s'%(datetime.today().date() + relativedelta(day=31))
        data = {'unfolded_lines': [], 
                'allow_domestic': False, 
                'fiscal_position': 'all', 
                'available_vat_fiscal_positions': [], 
                'date': {'string': format_my, 'period_type': 'month', 'mode': 'range', 'strict_range': False, 'date_from': date_from,'date_to': date_to, 'filter': 'this_month'}, 
                'analytic_accounts': [], 
                'selected_analytic_account_names': [], 
                'analytic_tags': [], 
                'selected_analytic_tag_names': [], 
                'hierarchy': False, 
                'unfold_all': False, 
                'headers': [[{'name': ''}, {'name': 'Reference'}, {'name': 'Partner'}, {'name': 'Balance', 'class': 'number'}]]}
        return data

    @api.model
    def check_report(self, data):
        currency_data = {
            'symbol': '',
            'position': 'after',
            'decimal_places': 2
        }

        report_lines = []
        col_need_format = ['credit', 'debit', 'balance', 'account_id',
                            'partner_id', 'cumulated_balance', 'amount_currency',
                            'progress', 'total_credit', 'total_debit', 'total_balance']
        col_need_format_aged_partner_banlance = ['direction', 'total', 'l0', 'l1', 'l2', 'l3', 'l4']
        options = {'decimal_precision': 'Account'}
        account_format = self.env['ir.qweb.field.float']
        if self.env.user.company_id and self.env.user.company_id.currency_id:
            company_id = self.env.user.company_id
            currency_data[
                'symbol'] = company_id.currency_id.symbol
            currency_data[
                'position'] = company_id.currency_id.position
            currency_data[
                'decimal_places'] = company_id.currency_id.decimal_places

        if data['report_type'] == 'config':
            if data['account_report_id'][1] == 'Analytic Report':
                data = self.prepare_data()
                ReportObj = self.env['account.analytic.report']
                report_lines = ReportObj.get_report_informations(options=data)
            else:
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_financial']
                report_lines = ReportObj.get_account_lines(data)
                for rec in report_lines:
                    rec['balance'] = account_format.value_to_html(rec.get('balance'),options).replace("\ufeff","")
        else:
            if data['account_report_id'][0] == 'journals_audit':
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_journal']

                target_move = data.get('target_move', 'all')
                sort_selection = data.get('sort_selection', 'date')

                report_lines = {}

                j_ids = []
                for i in data.get('journal_ids'):
                    j_ids.append(int(i))
                data['journal_ids'] = j_ids
                data['used_context']['journal_ids'] = j_ids

                for journal in j_ids:
                    report_lines[journal] = ReportObj.with_context(
                        data.get('used_context', {})).lines_dynamic(
                        target_move, journal, sort_selection,
                        {'form': data})
                    journal_obj = self.env[
                        'account.journal'].sudo().browse(
                        journal)
                    report_lines[journal] += [
                        ReportObj.get_total({'form': data}, journal_obj)]
                    report_lines[journal] += ReportObj.get_tax_declaration(
                        {'form': data}, journal_obj)
                for key, value in report_lines.items():
                    for val in value:
                        for col in col_need_format:
                            if col in val:
                                if isinstance(val[col], float):
                                    val[col] = account_format.value_to_html(val[col],options).replace("\ufeff","")
            elif data['account_report_id'][0] == 'partner_ledger':
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_partnerledger']

                res = ReportObj._get_partner_ids({'form': data})

                partner_ids = res[1]
                data = res[0]

                report_lines = ReportObj._dynamic_report_lines(data,
                                                               partner_ids)
                for re in report_lines:
                    for col in col_need_format:
                        if col in re:
                            if isinstance(re[col], float):
                                re[col] = account_format.value_to_html(re[col],options).replace("\ufeff","")
            elif data['account_report_id'][0] == 'general_ledger':
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_general_ledger']

                init_balance = data.get('initial_balance', True)
                sortby = data.get('sortby', 'sort_date')
                display_account = data.get('display_account', 'movement')

                codes = []
                if data.get('journal_ids', False):
                    codes = [journal.code for journal in
                             self.env['account.journal'].search(
                                 [('id', 'in', data['journal_ids'])])]
                partner_ids = data.get('partner_ids',False)

                analytic_accounts = [int(x) for x in data['account_analytic_ids']]
                if len(analytic_accounts) == 1:
                    analytic_accounts.append(0)
                accounts = self.env['account.account'].search([])
                analytic_account_ids = self.env['account.analytic.account'].search([('id', 'in' , analytic_accounts)])
                report_lines = ReportObj.with_context(
                    data.get('used_context', {})
                )._get_account_move_entry(accounts,analytic_account_ids,partner_ids,init_balance,sortby, display_account)
                for rec in report_lines:
                    for col in col_need_format:
                        if col in rec:
                            if isinstance(rec[col], float):
                                rec[col] = account_format.value_to_html(rec[col],options).replace("\ufeff","")
                    for r in rec['move_lines']:
                        for col in col_need_format:
                            if col in r:
                                if isinstance(r[col], float):
                                    r[col] = account_format.value_to_html(r[col],options).replace("\ufeff","")
            elif data['account_report_id'][0] == 'trial_balance':
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_trialbalance']

                display_account = data.get('display_account')
                accounts = self.env['account.account'].search([])
                analytic_account_ids = [int(x) for x in data['account_analytic_ids']]
                if len(analytic_account_ids) == 1:
                    analytic_account_ids.append(0)
                report_lines = ReportObj.with_context(
                    data.get('used_context')
                )._get_accounts_dynamic(accounts, display_account, analytic_account_ids)
                for rec in report_lines:
                    for col in col_need_format:
                        if col in rec:
                            if isinstance(rec[col], float):
                                rec[col] = account_format.value_to_html(rec[col],options).replace("\ufeff","")
            elif data['account_report_id'][0] == 'aged_partner':
                res = {}
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_agedpartnerbalance']

                # build the interval lines
                start = datetime.strptime(data.get('date_from'),
                                          '%Y-%m-%d')
                period_length = int(data['period_length'])

                for i in range(5)[::-1]:
                    stop = start - relativedelta(days=period_length - 1)
                    res[str(i)] = {
                        'name': (i != 0 and (str(
                            (5 - (i + 1)) * period_length) + '-' + str(
                            (5 - i) * period_length)) or (
                            '+' + str(4 * period_length))),
                        'stop': start.strftime('%Y-%m-%d'),
                        'start': (i != 0 and stop.strftime(
                            '%Y-%m-%d') or False),
                    }
                    start = stop - relativedelta(days=1)
                data.update(res)

                total = []

                target_move = data.get('target_move', 'all')
                date_from = data.get('date_from',
                                     time.strftime('%Y-%m-%d'))

                if data['result_selection'] == 'customer':
                    account_type = ['receivable']
                elif data['result_selection'] == 'supplier':
                    account_type = ['payable']
                else:
                    account_type = ['payable', 'receivable']
                
                partner_ids = data.get('partner_ids',False)

                movelines, total, dummy = ReportObj._get_partner_move_lines(
                    account_type,partner_ids, date_from, target_move,
                    int(data['period_length']))

                report_lines = ReportObj.dynamic_report_lines(data,
                                                              movelines,
                                                              total)
                for rec in report_lines:
                    for col in col_need_format_aged_partner_banlance:
                        if col in rec:
                            if isinstance(rec[col], (float, int)):
                                rec[col] = account_format.value_to_html(rec[col],options).replace("\ufeff","")
            elif data['account_report_id'][0] == 'tax_report':
                ReportObj = self.env[
                    'report.odb_account_reports_pdf.report_tax']

                lines = ReportObj.get_lines(data)

                report_lines = ReportObj.process_lines(lines)
                for rec in report_lines:
                    for col in ['net', 'tax']:
                        if col in rec:
                            if isinstance(rec[col], (float, int)):
                                rec[col] = account_format.value_to_html(rec[col],options).replace("\ufeff","")               

        return [report_lines, currency_data]

class ReportFinancialExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_financial'

    def _compute_journal_items(self, accounts,analytic_account_ids):
        """ compute the journal entries
        """
        res = {}
        # for account in accounts:
        #     res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            tables, where_clause, where_params = self.env[
                'account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            if len(analytic_account_ids) > 0:
                analytic_sql = 'AND (account_move_line.analytic_account_id in {})'.format(tuple(analytic_account_ids))
            else:
                analytic_sql = ''
            request = ("SELECT account_id,account_move_line.id as id," + 
                        "(SELECT account_analytic_account.name From account_analytic_account where account_move_line.analytic_account_id = account_analytic_account.id) as analytic_account_name," +
                        "(SELECT account_analytic_account.id From account_analytic_account where account_move_line.analytic_account_id = account_analytic_account.id) as analytic_account_id," +
                    "account_move_line.name,account_move_line.ref,"
                    " debit,credit," +
                    "debit-credit as balance" +
                    " FROM " + tables +
                    " WHERE account_id IN %s " +
                    filters + analytic_sql +
                    " GROUP BY account_id,account_move_line.id," +
                    "account_move_line.name,debit,"
                    "credit,account_move_line.ref")
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, reports,analytic_account_ids):
        '''returns a dictionary with key=the ID of a record
         and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with
                such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record
                (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(
                    report.account_ids,analytic_account_ids)
                res[report.id]['journal_items'] = self._compute_journal_items(
                    report.account_ids,analytic_account_ids)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search(
                    [('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(
                    accounts,analytic_account_ids)
                res[report.id]['journal_items'] = self._compute_journal_items(
                    accounts,analytic_account_ids)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id,analytic_account_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            # elif report.type == 'sum':
            #     # it's the sum of the children of this account.report
            #     res2 = self._compute_report_balance(report.children_ids)
            #     for key, value in res2.items():
            #         for field in fields:
            #             res[report.id][field] += value[field]
        return res

    def get_account_lines(self, data):
        lines = []
        analytic_account_ids = [int(x) for x in data['account_analytic_ids']]
        if len(analytic_account_ids) == 1:
            analytic_account_ids.append(0)
        account_report = self.env['account.financial.report'].search(
            [('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(
            data.get('used_context'))._compute_report_balance(child_reports,analytic_account_ids)

        fields = ['credit', 'debit', 'balance']
        m = child_reports.sorted(reverse=True)
        for i in m:
            if i.children_ids:
                a = dict(
                    filter(lambda x: (x[0] in i.children_ids.ids), res.items()))
                for key, val in res[i.id].items():
                    if key not in fields:
                        continue
                    res[i.id].update(
                        {key: sum(map(lambda dic_convert: dic_convert[1][key], a.items()))})

        if data['enable_filter']:
            comparison_res = self.with_context(
                data.get('comparison_context'))._compute_report_balance(
                child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get(
                            'account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * float(report.sign),
                'type': 'report',
                'level': bool(
                    report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False,
                'analytic_account': '',
                # used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * float(
                    report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                # the rest of the loop is used to display the details of
                # the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    # if there are accounts to display, we add them
                    # to the lines with a level equals to their level in
                    # the COA + 1 (to avoid having them with a too low
                    # level that would conflicts with the level of data
                    # financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * float(
                            report.sign) or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                        'analytic_account': '',
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(
                                vals['debit']
                        ) or not account.company_id.currency_id.is_zero(
                                vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(
                            vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * float(
                            report.sign)
                        if not account.company_id.currency_id.is_zero(
                                vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)

                    journal_items = self.fetch_journal_items(
                        account_id,
                        res[report.id].get('journal_items'),
                        vals['level'],
                        vals['name'],
                        data['debit_credit'])
                    if journal_items:
                        sub_lines += journal_items
                lines += sorted(sub_lines,
                                key=lambda sub_line: sub_line['name'])

        for rec in lines:
            if rec['type'] == 'journal_item':
                rec['name'] = rec['label']
                del rec['label']
        return lines

    def fetch_journal_items(self, account_id, journal_items, level, p_name,
                            debit_credit):
        result = []
        for rec in journal_items.values():
            if account_id == rec['account_id']:
                temp = {
                    'name': p_name,
                    'label': rec['name'] if rec['name'] else rec['ref'],
                    'level': level + 1,
                    'balance': rec['balance'],
                    'type': 'journal_item',
                    'line_id': rec['id'],
                    'analytic_account': rec['analytic_account_name'] or ''
                }
                if debit_credit:
                    temp['debit'] = rec['debit']
                    temp['credit'] = rec['credit']
                result.append(temp)
        return result


class ReportTaxExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_tax'

    def process_lines(self, lines):
        report_lines = [{
            'name': 'Sale',
            'net': 'Net',
            'tax': 'Tax',
            'level': 1,
            'parent': 0,
            'id': 1
        }]

        i = 0
        for line in lines['sale']:
            i += 1
            report_lines.append({
                'name': line.get('name'),
                'net': line.get('net'),
                'tax': line.get('tax'),
                'level': 2,
                'parent': 1,
                'id': i
            })

        i += 1
        report_lines.append({
            'name': 'Purchase',
            'net': ' ',
            'tax': ' ',
            'level': 1,
            'parent': 0,
            'id': i
        })

        parent = i
        for line in lines['purchase']:
            i += 1
            report_lines.append({
                'name': line.get('name'),
                'net': line.get('net'),
                'tax': line.get('tax'),
                'level': 2,
                'parent': parent,
                'id': i
            })
        return report_lines


class ReportAgedPartnerBalanceExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_agedpartnerbalance'

    def dynamic_report_lines(self, data, movelines, total):
        report_lines = []
        r_id = 1
        report_lines.append({
            'name': 'Partners',
            'direction': 'Not due',
            'l4': data['4']['name'],
            'l3': data['3']['name'],
            'l2': data['2']['name'],
            'l1': data['1']['name'],
            'l0': data['0']['name'],
            'total': 'Total',
            'line_type': 'font_bold',
            'id': r_id,
            'parent': 0
        })
        p_id = r_id
        if movelines:
            r_id += 1
            report_lines.append({
                'name': 'Account Total',
                'direction': total[6],
                'l4': total[4],
                'l3': total[3],
                'l2': total[2],
                'l1': total[1],
                'l0': total[0],
                'total': total[5],
                'line_type': 'font_bold',
                'id': r_id,
                'parent': 0
            })

            for rec in movelines:
                r_id += 1
                report_lines.append({
                    'name': rec['name'],
                    'direction': rec['direction'],
                    'l4': rec['4'],
                    'l3': rec['3'],
                    'l2': rec['2'],
                    'l1': rec['1'],
                    'l0': rec['0'],
                    'total': rec['total'],
                    'id': r_id,
                    'parent': 0
                })

        return report_lines


class ReportTrialBalanceExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_trialbalance'

    def _get_accounts_dynamic(self, accounts, display_account, analytic_account_ids):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or
                 those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and
                value.
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env[
            'account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        if len(analytic_account_ids) > 0:
            analytic_sql = 'AND (account_move_line.analytic_account_id in {})'.format(tuple(analytic_account_ids))
        else:
            analytic_sql = ''
        journal_items = (
            "SELECT account_move_line.id AS res_id, account_id, (SELECT account_analytic_account.name From account_analytic_account where account_move_line.analytic_account_id = account_analytic_account.id) as analytic_account_name," +
            "debit, credit, (debit - credit) AS" +
            " balance, account_move_line.ref, "
            "account_move_line.name as name " +
            " FROM " + tables +
            " WHERE account_id IN %s " + filters + analytic_sql +
            " GROUP BY account_id, account_move_line.id," +
            " account_move_line.name, account_move_line.debit," +
            " account_move_line.credit, account_move_line.ref")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(journal_items, params)
        journal_items = {}
        for rec in self.env.cr.dictfetchall():
            # rec['level'] = 2
            if rec['account_id'] in journal_items:
                journal_items[rec['account_id']].append(rec)
            else:
                journal_items[rec['account_id']] = [rec]

        if len(analytic_account_ids) > 0:
            analytic_sql = 'AND (account_move_line.analytic_account_id in {})'.format(tuple(analytic_account_ids))
        else:
            analytic_sql = ''
        request = ("SELECT account_id AS id, SUM(debit) AS debit, " +
                "SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS" +
                " balance FROM " + tables +
                " WHERE account_id IN %s " + filters + analytic_sql +
                " GROUP BY account_id")

        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        total_credit = 0.0
        total_debit = 0.0
        total_balance = 0.0
        total = {
            'line_type': 'total',
            'analytic_account_id': '',
            'total_credit': 0.0,
            'total_debit': 0.0,
            'total_balance': 0.0,
        }
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = (account.currency_id and account.currency_id or
                        account.company_id.currency_id)
            res['code'] = account.code
            res['name'] = account.name
            res['level'] = 1
            # res['res_id'] = account.id
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(
                        res['debit']) or not currency.is_zero(
                        res['credit'])):
                account_res.append(res)

            if account.id in journal_items:
                for j_line in journal_items[account.id]:
                    new_val = {
                        'level': 2,
                        'code': j_line['ref'] if j_line['ref'] else j_line[
                            'name'],
                        'name': account.name,
                        'debit': j_line['debit'],
                        'credit': j_line['credit'],
                        'balance': j_line['balance'],
                        'res_id': j_line['res_id'],
                        'line_type': 'journal_item',
                        'analytic_account_id': j_line['analytic_account_name'] or ''
                    }
                    account_res.append(new_val)
        for rc in account_res:
            if rc['level'] == 1:
                total_credit += rc.get('credit')
                total_debit += rc.get('debit')
                total_balance += rc.get('balance')
                rc['analytic_account_id'] = ''
        total.update({
            'line_type': 'total',
            'total_credit': total_credit,
            'total_debit': total_debit,
            'total_balance': total_balance,
        })
        account_res.append(total)
        return account_res


class ReportPartnerLedgerExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_partnerledger'

    def _get_partner_ref(self, partner_id):
        res = []
        if partner_id.ref:
            res.append(str(partner_id.ref))
        if partner_id.name:
            res.append(partner_id.name)
        return "-".join(res)

    def _dynamic_report_lines(self, data, partner_ids):
        result = []
        account_type = ''
        partner_id = [x.id for x in partner_ids]
        if len(data['computed']['ACCOUNT_TYPE']) > 1:
            account_type = 'in {}'.format(tuple(data['computed']['ACCOUNT_TYPE']))
        else:
            account_type = "= '{}'".format(data['computed']['ACCOUNT_TYPE'][0])
        params = [tuple(partner_id),data['form']['used_context']['company_id']]
        query_get_cumulated_balance = """
            SELECT account_move_line.id, (SELECT account_analytic_account.name From account_analytic_account where account_move_line.analytic_account_id = account_analytic_account.id) as analytic_account_name ,SUM(account_move_line.balance) OVER (ORDER BY account_move_line__partner_id.display_name DESC, account_move_line.id DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            FROM account_move_line LEFT JOIN res_partner AS account_move_line__partner_id ON (account_move_line.partner_id = account_move_line__partner_id.id)
            WHERE (account_move_line.partner_id in %s) AND (account_move_line.account_id in (SELECT account_account.id FROM account_account WHERE (account_account.internal_type """ + account_type + """) AND (account_account.company_id IS NULL  OR (account_account.company_id = (%s)))))
        """
        self.env.cr.execute(query_get_cumulated_balance, tuple(params))
        res = self.env.cr.dictfetchall()
        for p_id in partner_ids:
            result.append({
                'line_type': 'section_heading',
                'date': self._get_partner_ref(p_id),
                'analytic_account_id': '',
                'debit':self._sum_partner(data, p_id, 'debit'),
                'credit': self._sum_partner(data, p_id, 'credit'),
                'balance': self._sum_partner(data, p_id, 'debit - credit'),
            })
            result += self._lines(data, p_id)
        for re in result:
            if re.get('id'):
                for r in res:
                    if re.get('id') == r.get('id'):
                        re['cumulated_balance'] = r.get('sum')
                        re['analytic_account_id'] = r.get('analytic_account_name') or ''
        return result

    def _get_partner_ids(self, data=None):
        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
        SELECT a.id
        FROM account_account a
        WHERE a.internal_type IN %s
        AND NOT a.deprecated""",
                            (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in
                                           self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + query_get_data[
            2]
        reconcile_clause = "" if data['form'][
            'reconciled'
        ] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
        SELECT DISTINCT "account_move_line".partner_id
        FROM """ + query_get_data[0] + """, account_account AS account,
         account_move AS am
        WHERE "account_move_line".partner_id IS NOT NULL
            AND "account_move_line".account_id = account.id
            AND am.id = "account_move_line".move_id
            AND am.state IN %s
            AND "account_move_line".account_id IN %s
            AND NOT account.deprecated
            AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in
                       self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners,
                          key=lambda x: (x.ref or '', x.name or ''))

        return [data, partners]


class ReportJournalExt(models.AbstractModel):
    _inherit = 'report.odb_account_reports_pdf.report_journal'

    def get_total(self, data, journal_id):
        return {
            'line_type': 'font_bold',
            'move_id': 'Total',
            'date': "",
            'account_id': "",
            'partner_id': '',
            'name': '',
            'analytic_account_id': '',
            'debit': self._sum_debit(data, journal_id),
            'credit': self._sum_credit(data, journal_id),
        }

    def get_tax_declaration(self, data, journal_id):
        result = list()

        result.append({
            'line_type': 'font_bold',
            'move_id': 'Tax Declaration',
            'date': "",
            'account_id': "",
            'partner_id': '',
            'name': '',
            'analytic_account_id': '',
            'debit': "",
            'credit': "",
        })

        result.append({
            'line_type': 'font_bold',
            'move_id': 'name',
            'date': "",
            'account_id': "Base Amount",
            'partner_id': 'Tax Amount',
            'name': '',
            'analytic_account_id': '',
            'debit': "",
            'credit': "",
        })

        taxes = self._get_taxes(data, journal_id)
        for tax in taxes:
            result.append({
                'line_type': 'font_bold',
                'move_id': tax.name,
                'date': "",
                'account_id': self.env['ir.qweb.field.float'].value_to_html(taxes[tax]['base_amount'],{'decimal_precision': 'Account'}).replace("\ufeff",""),
                'partner_id': self.env['ir.qweb.field.float'].value_to_html(taxes[tax]['tax_amount'],{'decimal_precision': 'Account'}).replace("\ufeff",""),
                'name': '',
                'analytic_account_id': '',
                'debit': "",
                'credit': "",
            })

        return result

    def lines_dynamic(self, target_move, journal_ids, sort_selection,
                      data):
        if isinstance(journal_ids, int):
            journal_ids = [journal_ids]

        analytic_account_ids = [int(x) for x in data['form']['account_analytic_ids']]
        if len(analytic_account_ids) > 0:
            analytic_account_ids.append(0)
            analytic_sql = '(account_move_line.analytic_account_id in {}) AND'.format(tuple(analytic_account_ids))
        else:
            analytic_sql = ''
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_ids)] + \
            query_get_clause[2]
        query = ('SELECT "account_move_line".id FROM ' + query_get_clause[
            0] +
            ', account_move am, account_account acc WHERE ' +
            '"account_move_line".account_id = acc.id AND ' +
            '"account_move_line".move_id=am.id AND am.state IN %s AND ' +
            '"account_move_line".journal_id IN %s AND ' + analytic_sql +
            query_get_clause[1] + ' ORDER BY ')
        if sort_selection == 'date':
            query += '"account_move_line".date'
        else:
            query += 'am.name'
        query += ', "account_move_line".move_id, acc.code'

        self.env.cr.execute(query, tuple(params))
        ids = (x[0] for x in self.env.cr.fetchall())

        result = []
        target_fields = ['id', 'move_id', 'date', 'account_id',
                         'partner_id',
                         'name', 'debit', 'credit', 'currency_id', 'analytic_account_id']

        for rec in self.env['account.move.line'].browse(ids):
            temp = {}
            for f_key in target_fields:
                if f_key in ['move_id', 'partner_id']:
                    temp[f_key] = rec[f_key].name if rec[f_key] else ""
                elif f_key == 'currency_id':
                    temp[f_key] = rec[f_key].symbol if rec[f_key] else ""
                elif f_key == 'id':
                    temp['res_id'] = rec[f_key]
                elif f_key == 'account_id':
                    temp[f_key] = rec[f_key].code if rec[f_key] else ""
                elif f_key == 'debit':
                    temp[f_key] = rec[f_key]
                elif f_key == 'credit':
                    temp[f_key] = rec[f_key]
                elif f_key == 'analytic_account_id':
                    temp[f_key] = rec[f_key].name or ''
                else:
                    temp[f_key] = rec[f_key]
            result += [temp]
        return result
