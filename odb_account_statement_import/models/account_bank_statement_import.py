# -*- coding: utf-8 -*-
import base64

import io
import logging, copy
import tempfile
import binascii
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _description = 'Import Bank Statement'

    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True,
                                      help='Get you bank statements in electronic format from your bank and'
                                           ' select them here.')

    action_type = fields.Selection(
        string='Action Import', required=True,
        selection=[('opt1', 'No Action'), ('opt2', 'Post Statement'),
                   ('opt3', 'Validate Reconcile')]
    )

    def get_partner(self, value):
        partner = self.env['res.partner'].search([('name', '=', value)])
        return partner.id if partner else False

    def get_currency(self, value):
        currency = self.env['res.currency'].search([('name', '=', value)])
        return currency.id if currency else False

    def get_account(self, value):
        account = self.env['account.account'].search([('code', '=', value)])
        return account.id if account else False

    def get_tax(self, value):
        return self.env['account.tax'].search([('name', '=', value)])
    
    def get_group_analytic(self,value):
        return self.env['account.analytic.group'].search([('name','=',value)])
    
    def get_product(self,value):
        product = self.env['product.product'].search([('barcode','=',value)])
        return product.id if product else False

    def get_account_analytic(self, value):
        analytic = self.env['account.analytic.account'].search(
            [('name', '=', value)])
        return analytic.id if analytic else False

    def get_analytic_tag_ids(self, value):
        tag = self.env['account.analytic.tag'].search([('name', '=', value)])
        return [[6, 0, tag.ids]] if tag else []

    def create_statement(self, values):
        statement = self.env['account.bank.statement'].create(values)
        return statement

    def action_statement_post(self, statement):
        statement.update({
            'balance_end_real': statement.balance_start + statement.total_entry_encoding
        })
        statement.button_post()
    


    @api.model
    def _check_debit_credit_move_line_vals(self,st_line):
        ''' Prepare values to create a new account.move.line record corresponding to the
        liquidity line (having the bank/cash account).
        :return:        The values to create a new account.move.line record.
        '''
        self.ensure_one()

        statement = st_line.statement_id
        journal = statement.journal_id
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id or company_currency

        if st_line.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            if st_line.foreign_currency_id == company_currency:
                amount_currency = st_line.amount
                balance = st_line.amount_currency
            else:
                amount_currency = st_line.amount
                balance = journal_currency._convert(amount_currency, company_currency, journal.company_id, st_line.date)
        elif st_line.foreign_currency_id and not journal_currency:
            amount_currency = st_line.amount_currency
            balance = st_line.amount
            currency_id = st_line.foreign_currency_id.id
        elif not st_line.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            amount_currency = st_line.amount
            balance = journal_currency._convert(amount_currency, journal.company_id.currency_id, journal.company_id, st_line.date)
        else:
            currency_id = company_currency.id
            amount_currency = st_line.amount
            balance = st_line.amount

        return {
            # 'name': self.payment_ref,
            # 'move_id': self.move_id.id,
            # 'partner_id': self.partner_id.id,
            # 'currency_id': currency_id,
            # 'account_id': journal.default_account_id.id,
            'debit': balance > 0 and balance or 0.0,
            'credit': balance < 0 and -balance or 0.0,
            # 'amount_currency': amount_currency,
        }


    @api.model
    def _prepare_aml_dict(self,group_counterpart_aml):
        list_aml_dict ={}
        for key,val in group_counterpart_aml.items():
            if key == 'id':
                list_aml_dict['counterpart_aml_id'] = val
            if key in ['name','debit','credit']:
                list_aml_dict[key] = val
            
        if list_aml_dict['debit'] > list_aml_dict['credit']:
            c = list_aml_dict['debit']
            d = list_aml_dict['credit']
            list_aml_dict['debit'] = d
            list_aml_dict['credit'] = c
        list_aml_dict['analytic_tag_ids'] = [[6,None,[]]]
        return list_aml_dict

    def _update_value(self,result,list_update,st_line,list_new_dict_vat,list_new_dict):
        '''Cập nhật lại giá trị cho list_new_dict và value cho list_new_dict_vat '''
        if list_update['base'] - st_line.amount < 0:
            if result['debit'] > 0:
                list_new_dict_vat['debit']= 0
                list_new_dict_vat['credit']= list_update['amount']
                list_new_dict['credit'] = list_update['base']
            elif result['credit'] > 0:
                list_new_dict_vat['credit']= 0
                list_new_dict_vat['debit']= list_update['amount']
                list_new_dict['debit'] = list_update['base']   
            
        else:
            if result['debit'] > 0:
                list_new_dict_vat['debit']= 0
                list_new_dict_vat['credit']= abs(list_update['amount'])
                if list_update['base'] < 0 and abs(list_update['base']) <  abs(st_line.amount): 
                    list_new_dict['credit'] = abs(list_update['base']) 
                else:
                    list_new_dict['credit'] = list_update['base'] - st_line.amount 
            elif result['credit'] > 0:
                list_new_dict_vat['credit']= 0
                list_new_dict_vat['debit']= abs(list_update['amount'])
                if list_update['base'] < 0 and abs(list_update['base']) < abs(st_line.amount):
                    list_new_dict['debit'] = abs(list_update['base'])
                else:
                    list_new_dict['debit'] = list_update['base'] - st_line.amount

    def _init_value_to_tax(self,tax_defs,list_new_dict_vat,list_new_dict):
        '''Khởi tạo value cho list_new_dict_vat khi có thuế.'''
        list_update = tax_defs['taxes'][0]
        list_new_dict_vat['name'] = list_new_dict['name'] + ' ' +list_update['name']
        list_new_dict_vat['debit']= list_update['amount']
        list_new_dict_vat['analytic_tag_ids'] = [[6,None,[]]]
        list_new_dict_vat['account_id'] = list_update['account_id']
        list_new_dict_vat['tax_repartition_line_id'] = list_update['tax_repartition_line_id']
        list_new_dict_vat['tax_tag_ids'] = [[(6, None, list_update['tax_ids'])]] if list_update['tax_ids'] else [[(6, None, [])]] 
        list_new_dict_vat['tax_ids'] == []
        if 'tax_ids' in list_new_dict_vat:
            list_new_dict_vat.pop('tax_ids')

    def compute_val(self,statement=None,st_line=None):
        group_new_aml_dicts= []
        group_counterpart_aml=[]
        new_aml_dicts = []
        
        load_data = self.env['account.reconciliation.widget'].get_bank_statement_line_data(st_line.ids)
        group_new_aml_dicts.append(load_data['lines'][0]['st_line'])
        reconciliation_proposition = load_data['lines'][0]['reconciliation_proposition'] 
        # Prepsre computer aml dict
        counterpart_aml_dicts = {}
        if reconciliation_proposition:
            # group_counterpart_aml.append(reconciliation_proposition[0])
            counterpart_aml_dicts['counterpart_aml_dicts'] = [self._prepare_aml_dict(rec) for rec in reconciliation_proposition]
        else:
            counterpart_aml_dicts['counterpart_aml_dicts'] = []
            
        # Prepsre new aml dict
        # Khởi tạo move line chưa tính thuế
        list_new_dict ={}
        for key,val in group_new_aml_dicts[0].items():
            if key in ['name']:
                list_new_dict[key] = val
        
        result = self._check_debit_credit_move_line_vals(st_line)  
        if not reconciliation_proposition:
            if result['debit'] > 0:
                list_new_dict['debit'] = 0.0
                list_new_dict['credit'] = result['debit']
            if result['credit'] > 0:
                list_new_dict['debit'] = result['credit']
                list_new_dict['credit'] = 0.0
            
        else:
            if len(reconciliation_proposition) >1:
                if result['debit'] > 0:
                    list_new_dict['debit'] = 0.0
                    list_new_dict['credit'] =abs(group_new_aml_dicts[0]['amount']) - abs(sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]))
                if result['credit'] > 0:
                    list_new_dict['debit'] = abs(group_new_aml_dicts[0]['amount']) - abs(sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]))
                    list_new_dict['credit'] = 0.0
            else:
                if result['debit'] > 0:
                    list_new_dict['debit'] = 0.0
                    list_new_dict['credit'] = reconciliation_proposition[0]['debit']
                if result['credit'] > 0:
                    list_new_dict['debit'] =  reconciliation_proposition[0]['debit']
                    list_new_dict['credit'] = 0.0

        list_new_dict['account_id'] = [st_line.account_id.id if st_line.account_id else False][0]
        list_new_dict['analytic_account_id'] = st_line.analytic_account_id.id if st_line.analytic_account_id else False
        list_new_dict['analytic_tag_ids'] = [[(6, None, st_line.analytic_tag_ids.ids)]] if st_line.analytic_tag_ids else [[(6, None, [])]]
        
        list_new_dict['tax_ids'] =[[(6, None, st_line.tax_ids.ids)]] if st_line.tax_ids else [[(6, None, [])]]
        if st_line.tax_ids:
            a = [x for x in st_line.tax_ids.tax_group_id.name if x.isdigit()]
            if a:
                tax_tag_ids = self.env['account.account.tag'].search([('name','like',a[0]),('name','like',st_line.tax_ids.type_tax_use.title()),('name','like','Untaxed')])[0]
            else:
                tax_tag_ids = self.env['account.account.tag'].search([('name','like',st_line.tax_ids.type_tax_use.title()),('name','like','Untaxed')])[0]
        else:
            tax_tag_ids = self.env['account.account.tag'].search([('name','like','Untaxed')])[0]

        list_new_dict['tax_tag_ids'] =[[(6, None, tax_tag_ids.ids)]] if tax_tag_ids else [[(6, None, [])]]
        
        # Khởi tạo move line áp thuế  ( VD: Deductible VAT 5%)
            # tính inclue tax
            # có ba yếu tố để tính tax, 
                # + reconciliation_proposition
                # + tax_ids
                # + Giá trị trả về từ hàm '_check_debit_credit_move_line_vals()' để xác đính credit và debit 
        if reconciliation_proposition:
            if st_line.tax_ids and st_line.force_tax_included:
                list_new_dict_vat = copy.deepcopy(list_new_dict)

                tax_defs = st_line.tax_ids.with_context(force_price_include=True,
                            round=True,journal_id=statement.journal_id.id,
                            caba_no_transition_account = True,
                            statement_line_ids=self.env['account.bank.statement.line'].search([]).ids).json_friendly_compute_all(
                                    price_unit=[ sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]) if reconciliation_proposition else group_new_aml_dicts[0]['amount']][0],
                                    currency_id = st_line.currency_id.id,is_refund=False,include_caba_tags=False)

                 # update value list_new_dict not VAT                                                                        
                list_update = tax_defs['taxes'][0]
                self._init_value_to_tax(tax_defs,list_new_dict_vat,list_new_dict)                                                                     
                self._update_value(result,list_update,st_line,list_new_dict_vat,list_new_dict)


            elif st_line.tax_ids and not st_line.force_tax_included:
                tax_defs = st_line.tax_ids.with_context(force_price_include=False,
                            round=True,journal_id=statement.journal_id.id,
                            caba_no_transition_account = True,
                            statement_line_ids=self.env['account.bank.statement.line'].search([]).ids).json_friendly_compute_all(
                                    price_unit=[ sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]) if reconciliation_proposition else group_new_aml_dicts[0]['amount']][0],
                                    currency_id = st_line.currency_id.id,is_refund=False,include_caba_tags=False)

                # update value list_new_dict not VAT
                list_update = tax_defs['taxes'][0]
                self._init_value_to_tax(tax_defs,list_new_dict_vat,list_new_dict)
                self._update_value(result,list_update,st_line,list_new_dict_vat,list_new_dict)

            else:
                list_new_dict_vat = []

        else:
            if st_line.tax_ids and st_line.force_tax_included:
                list_new_dict_vat = copy.deepcopy(list_new_dict)

                tax_defs = st_line.tax_ids.with_context(force_price_include=True,
                            round=True,journal_id=statement.journal_id.id,
                            caba_no_transition_account = True,
                            statement_line_ids=self.env['account.bank.statement.line'].search([]).ids).json_friendly_compute_all(
                                    price_unit=[ sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]) if reconciliation_proposition else group_new_aml_dicts[0]['amount']][0],
                                    currency_id = st_line.currency_id.id,is_refund=False,include_caba_tags=False)

                # update value list_new_dict not VAT
                list_update = tax_defs['taxes'][0]
                self._init_value_to_tax(tax_defs,list_new_dict_vat,list_new_dict)
                self._update_value(result,list_update,st_line,list_new_dict_vat,list_new_dict)

            elif st_line.tax_ids and st_line.force_tax_included:
                tax_defs = st_line.tax_ids.with_context(force_price_include=False,
                            round=True,journal_id=statement.journal_id.id,
                            caba_no_transition_account = True,
                            statement_line_ids=self.env['account.bank.statement.line'].search([]).ids).json_friendly_compute_all(
                                    price_unit=[ sum([rec['debit'] for rec in reconciliation_proposition if rec['debit'] ]) if reconciliation_proposition else group_new_aml_dicts[0]['amount']][0],
                                    currency_id = st_line.currency_id.id,is_refund=False,include_caba_tags=False)

                # update value list_new_dict not VAT
                list_update = tax_defs['taxes'][0]
                self._init_value_to_tax(tax_defs,list_new_dict_vat,list_new_dict)
                self._update_value(result,list_update,st_line,list_new_dict_vat,list_new_dict)

            else:
                list_new_dict_vat = []


        new_aml_dicts ={}
        if list_new_dict_vat != []:
            new_aml_dicts['new_aml_dicts'] =[list_new_dict,list_new_dict_vat]
        else:
            new_aml_dicts['new_aml_dicts'] =[list_new_dict]

        group_total={}
        group_total['counterpart_aml_dicts'] = counterpart_aml_dicts['counterpart_aml_dicts']
        group_total['new_aml_dicts'] = new_aml_dicts['new_aml_dicts']
        group_total['payment_aml_ids'] = []
        group_total['partner_id'] = st_line.partner_id.id
        group_total['to_check'] = False
        data = [group_total]
        
        return data
        
    def import_file(self):
        for data_file in self.attachment_ids:
            file_name = data_file.name.lower()
            try:
                if file_name.strip().endswith('.csv') or file_name.strip().endswith('.xlsx'):
                    statement = False
                    if file_name.strip().endswith('.csv'):
                        keys = ['date', 'payment_ref',
                                'partner_id', 'amount', 'currency_id']
                        try:
                            csv_data = base64.b64decode(data_file.datas)
                            data_file = io.StringIO(csv_data.decode("utf-8"))
                            data_file.seek(0)
                            file_reader = []
                            values = {}
                            csv_reader = csv.reader(data_file, delimiter=',')
                            file_reader.extend(csv_reader)
                        except:
                            raise UserError(_("Invalid file!"))
                        vals_list = []
                        date = False
                        for i in range(len(file_reader)):
                            field = list(map(str, file_reader[i]))
                            values = dict(zip(keys, field))
                            if values:
                                if i == 0:
                                    continue
                                else:
                                    if not date:
                                        date = field[0]
                                    values.update({
                                        'date': field[0],
                                        'payment_ref': field[1],
                                        'ref': field[2],
                                        'partner_id': self.get_partner(field[3]),
                                        'amount': field[4],
                                        'currency_id':  self.get_currency(field[5])
                                    })
                                    vals_list.append((0, 0, values))
                        statement_vals = {
                            'name': 'Statement Of ' + str(datetime.today().date()),
                            'journal_id': self.env.context.get('active_id'),
                            'line_ids': vals_list
                        }
                        if len(vals_list) != 0:
                            statement = self.create_statement(statement_vals)
                    elif file_name.strip().endswith('.xlsx'):
                        try:
                            fp = tempfile.NamedTemporaryFile(
                                delete=False, suffix=".xlsx")
                            fp.write(binascii.a2b_base64(data_file.datas))
                            fp.seek(0)
                            values = {}
                            workbook = xlrd.open_workbook(fp.name)
                            sheet = workbook.sheet_by_index(0)
                        except:
                            raise UserError(_("Invalid file!"))
                        vals_list = []
                        counter = 0
                        skipped_line_no = {}
                        erro_convert=[]
                        for row_no in range(sheet.nrows):
                            val = {}
                            values = {}
                            if row_no <= 0:
                                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                            else:
                                # line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                #     row.value), sheet.row(row_no)))
                                line = [sheet.cell_value(row_no, cell) for cell in range(sheet.ncols)]
                                tax_id = self.get_tax(line[7])
                                account= self.get_account(int(line[6]))
                                if not account:
                                    skipped_line_no[str(row_no)] = _({'Account not found':str(line[6])})
                                    erro_convert.append(row_no)
                                    continue
                                values.update({
                                    'date': line[0],
                                    'payment_ref': line[1],
                                    'ref': line[2],
                                    'partner_id': self.get_partner(line[3]),
                                    'amount': line[4],
                                    'currency_id': self.get_currency(line[5]),
                                    'account_id': account,
                                    'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                    'force_tax_included': True if line[8] and tax_id else False,
                                    'analytic_account_id': self.get_account_analytic(line[9]),
                                    'analytic_tag_ids': self.get_analytic_tag_ids(line[10]),
                                })
                                vals_list.append((0, 0, values))
                        statement_vals = {
                            'name': 'Statement Of ' + str(datetime.today().date()),
                            'date': str(datetime.today().date()),
                            'journal_id': self.env.context.get('active_id'),
                            'line_ids': vals_list
                        }
                        if len(vals_list) != 0:
                            statement = self.create_statement(statement_vals)
                        if statement:
                            if self.action_type == 'opt2':
                                self.action_statement_post(statement)
                            if self.action_type == 'opt3':
                                self.action_statement_post(statement)

                                for st_line in statement.line_ids:
                                    try:
                                        data = self.compute_val(statement,st_line)

                                        self.env['account.reconciliation.widget'].process_bank_statement_line(st_line.ids,data)
                                        counter +=1
    
                                    except Exception as e:
                                        skipped_line_no[str(counter + 1)] = _({st_line.ref: str(e)})
                                        counter +=1
                                        dic_msg = ''
                                        if skipped_line_no:
                                            dic_msg = dic_msg + "Errors (%s):" % str(len(skipped_line_no) + 1)
                                            for k, v in skipped_line_no.items():
                                                dic_msg = dic_msg + "\nRow. " + k + v
                                        dic_msg = dic_msg + _("\nRow. " + str(counter) + " - SourceCodeError: " + str(e))
                                        continue
                                # statement.button_validate_or_action()
                                if counter > 1:
                                    if erro_convert:
                                        completed_records = (counter + len(erro_convert) - len(skipped_line_no))
                                    else: 
                                        completed_records = (counter - len(skipped_line_no))
                                    res = self.show_success_msg(
                                        completed_records, skipped_line_no)
                                return res

                        # return {
                        #     'type': 'ir.actions.act_window',
                        #     'res_model': 'account.bank.statement',
                        #     'view_mode': 'form',
                        #     'res_id': statement.id,
                        #     'views': [(False, 'form')],
                        # }
                else:
                    raise ValidationError(_("Unsupported File Type"))
            except Exception as e:
                raise ValidationError(_(e))

    def show_success_msg(self, counter, skipped_line_no):
        # open the new success message box
        view = self.env.ref('odb_base.wizard_message_popup')
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k, v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow " + k + " " + v + " "
        context['message'] = dic_msg

        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.message.popup',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    # def import_file(self):
    #     """ Process the file chosen in the wizard, create bank statement(s) and go to reconciliation. """
    #     self.ensure_one()
    #     statement_line_ids_all = []
    #     notifications_all = []
    #     # Let the appropriate implementation module parse the file and return the required data
    #     # The active_id is passed in context in case an implementation module requires information about the wizard state (see QIF)
    #     for data_file in self.attachment_ids:
    #         currency_code, account_number, stmts_vals = self.with_context(active_id=self.ids[0])._parse_file(base64.b64decode(data_file.datas))
    #         # Check raw data
    #         self._check_parsed_data(stmts_vals, account_number)
    #         # Try to find the currency and journal in odoo
    #         currency, journal = self._find_additional_data(currency_code, account_number)
    #         # If no journal found, ask the user about creating one
    #         if not journal:
    #             # The active_id is passed in context so the wizard can call import_file again once the journal is created
    #             return self.with_context(active_id=self.ids[0])._journal_creation_wizard(currency, account_number)
    #         if not journal.default_debit_account_id or not journal.default_credit_account_id:
    #             raise UserError(_('You have to set a Default Debit Account and a Default Credit Account for the journal: %s') % (journal.name,))
    #         # Prepare statement data to be used for bank statements creation
    #         stmts_vals = self._complete_stmts_vals(stmts_vals, journal, account_number)
    #         # Create the bank statements
    #         statement_line_ids, notifications = self._create_bank_statements(stmts_vals)
    #         statement_line_ids_all.extend(statement_line_ids)
    #         notifications_all.extend(notifications)
    #         # Now that the import worked out, set it as the bank_statements_source of the journal
    #         if journal.bank_statements_source != 'file_import':
    #             # Use sudo() because only 'account.group_account_manager'
    #             # has write access on 'account.journal', but 'account.group_account_user'
    #             # must be able to import bank statement files
    #             journal.sudo().bank_statements_source = 'file_import'
    #     # Finally dispatch to reconciliation interface
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'bank_statement_reconciliation_view',
    #         'context': {'statement_line_ids': statement_line_ids_all,
    #                     'company_ids': self.env.user.company_ids.ids,
    #                     'notifications': notifications_all,
    #         },
    #     }

    def _journal_creation_wizard(self, currency, account_number):
        """ Calls a wizard that allows the user to carry on with journal creation """
        return {
            'name': _('Journal Creation'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.import.journal.creation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'statement_import_transient_id': self.env.context['active_id'],
                'default_bank_acc_number': account_number,
                'default_name': _('Bank') + ' ' + account_number,
                'default_currency_id': currency and currency.id or False,
                'default_type': 'bank',
            }
        }

    def _parse_file(self, data_file):

        raise UserError(
            _('Could not make sense of the given file.\nDid you install the module to support this type of file ?'))

    def _check_parsed_data(self, stmts_vals, account_number):
        """ Basic and structural verifications """
        extra_msg = _(
            'If it contains transactions for more than one account, it must be imported on each of them.')
        if len(stmts_vals) == 0:
            raise UserError(
                _('This file doesn\'t contain any statement for account %s.') % (
                    account_number,)
                + '\n' + extra_msg
            )

        no_st_line = True
        for vals in stmts_vals:
            if vals['transactions'] and len(vals['transactions']) > 0:
                no_st_line = False
                break
        if no_st_line:
            raise UserError(
                _('This file doesn\'t contain any transaction for account %s.') % (
                    account_number,)
                + '\n' + extra_msg
            )

    def _check_journal_bank_account(self, journal, account_number):
        # Needed for CH to accommodate for non-unique account numbers
        sanitized_acc_number = journal.bank_account_id.sanitized_acc_number
        if " " in sanitized_acc_number:
            sanitized_acc_number = sanitized_acc_number.split(" ")[0]
        return sanitized_acc_number == account_number

    def _find_additional_data(self, currency_code, account_number):
        """ Look for a res.currency and account.journal using values extracted from the
            statement and make sure it's consistent.
        """
        company_currency = self.env.company.currency_id
        journal_obj = self.env['account.journal']
        currency = None
        sanitized_account_number = sanitize_account_number(account_number)

        if currency_code:
            currency = self.env['res.currency'].search(
                [('name', '=ilike', currency_code)], limit=1)
            if not currency:
                raise UserError(
                    _("No currency found matching '%s'.") % currency_code)
            if currency == company_currency:
                currency = False

        journal = journal_obj.browse(self.env.context.get('journal_id', []))
        if account_number:
            # No bank account on the journal : create one from the account number of the statement
            if journal and not journal.bank_account_id:
                journal.set_bank_account(account_number)
            # No journal passed to the wizard : try to find one using the account number of the statement
            elif not journal:
                journal = journal_obj.search(
                    [('bank_account_id.sanitized_acc_number', '=', sanitized_account_number)])
            # Already a bank account on the journal : check it's the same as on the statement
            else:
                if not self._check_journal_bank_account(journal, sanitized_account_number):
                    raise UserError(_('The account of this statement (%s) is not the same as the journal (%s).') % (
                        account_number, journal.bank_account_id.acc_number))

        # If importing into an existing journal, its currency must be the same as the bank statement
        if journal:
            journal_currency = journal.currency_id
            if currency is None:
                currency = journal_currency
            if currency and currency != journal_currency:
                statement_cur_code = not currency and company_currency.name or currency.name
                journal_cur_code = not journal_currency and company_currency.name or journal_currency.name
                raise UserError(_('The currency of the bank statement (%s) is not the same as the currency of the journal (%s).') % (
                    statement_cur_code, journal_cur_code))

        # If we couldn't find / can't create a journal, everything is lost
        if not journal and not account_number:
            raise UserError(
                _('Cannot find in which journal import this statement. Please manually select a journal.'))

        return currency, journal

    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        for st_vals in stmts_vals:
            st_vals['journal_id'] = journal.id
            if not st_vals.get('reference'):
                st_vals['reference'] = " ".join(
                    self.attachment_ids.mapped('name'))
            if st_vals.get('number'):
                # build the full name like BNK/2016/00135 by just giving the number '135'
                st_vals['name'] = journal.sequence_id.with_context(
                    ir_sequence_date=st_vals.get('date')).get_next_char(st_vals['number'])
                del(st_vals['number'])
            for line_vals in st_vals['transactions']:
                unique_import_id = line_vals.get('unique_import_id')
                if unique_import_id:
                    sanitized_account_number = sanitize_account_number(
                        account_number)
                    line_vals['unique_import_id'] = (
                        sanitized_account_number and sanitized_account_number + '-' or '') + str(journal.id) + '-' + unique_import_id

                if not line_vals.get('bank_account_id'):
                    # Find the partner and his bank account or create the bank account. The partner selected during the
                    # reconciliation process will be linked to the bank when the statement is closed.
                    identifying_string = line_vals.get('account_number')
                    if identifying_string:
                        partner_bank = self.env['res.partner.bank'].search(
                            [('acc_number', '=', identifying_string)], limit=1)
                        if partner_bank:
                            line_vals['bank_account_id'] = partner_bank.id
                            line_vals['partner_id'] = partner_bank.partner_id.id
        return stmts_vals

    def _create_bank_statements(self, stmts_vals):
        """ Create new bank statements from imported values, filtering out already imported transactions, and returns data used by the reconciliation widget """
        BankStatement = self.env['account.bank.statement']
        BankStatementLine = self.env['account.bank.statement.line']

        # Filter out already imported transactions and create statements
        statement_line_ids = []
        ignored_statement_lines_import_ids = []
        for st_vals in stmts_vals:
            filtered_st_lines = []
            for line_vals in st_vals['transactions']:
                if 'unique_import_id' not in line_vals \
                   or not line_vals['unique_import_id'] \
                   or not bool(BankStatementLine.sudo().search([('unique_import_id', '=', line_vals['unique_import_id'])], limit=1)):
                    filtered_st_lines.append(line_vals)
                else:
                    ignored_statement_lines_import_ids.append(
                        line_vals['unique_import_id'])
                    if 'balance_start' in st_vals:
                        st_vals['balance_start'] += float(line_vals['amount'])

            if len(filtered_st_lines) > 0:
                # Remove values that won't be used to create records
                st_vals.pop('transactions', None)
                # Create the statement
                st_vals['line_ids'] = [[0, False, line]
                                       for line in filtered_st_lines]
                statement_line_ids.extend(
                    BankStatement.create(st_vals).line_ids.ids)
        if len(statement_line_ids) == 0:
            raise UserError(_('You already have imported that file.'))

        # Prepare import feedback
        notifications = []
        num_ignored = len(ignored_statement_lines_import_ids)
        if num_ignored > 0:
            notifications += [{
                'type': 'warning',
                'message': _("%d transactions had already been imported and were ignored.") % num_ignored if num_ignored > 1 else _("1 transaction had already been imported and was ignored."),
                'details': {
                    'name': _('Already imported items'),
                    'model': 'account.bank.statement.line',
                    'ids': BankStatementLine.search([('unique_import_id', 'in', ignored_statement_lines_import_ids)]).ids
                }
            }]
        return statement_line_ids, notifications
