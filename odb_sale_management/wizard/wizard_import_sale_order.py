# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64,xlrd,logging
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import itertools
from operator import itemgetter
from odoo.tools.safe_eval import safe_eval, time
_logger = logging.getLogger(__name__)

class ImportSOLWizard(models.TransientModel):
    _name = "wizard.import.sale.order"
    _description = "Import Sale Order Wizard"

    def get_default(self):
        if self._context.get('import_type'):
            return self._context.get('import_type')
        else:
            return 'sale_order'

    file = fields.Binary(string="File",)
    import_type = fields.Selection([
        ('sale_order', 'Sale Order'),
        ('sale_line', 'Sale Order Line'),
        ('export','Export Order')
    ], default=get_default, string="Import File Type", required=True)
    is_select_file = fields.Boolean(string='Select File')    
    attachment_id = fields.Many2one('ir.attachment', 'Select File')

    sale_order_ids = fields.Many2many('sale.order', string='Select order')
    sale_order_id = fields.Many2one('sale.order',string='Select Sale Order')

    @api.onchange('is_select_file')
    def get_value(self):
        domain = {'attachment_id': []}
        if self.is_select_file:
            order_id = self.env.context.get('sale_id')
            model = self.env.context.get('active_model')
            domain = {'attachment_id': [('res_id','=',order_id),('res_model','=',model),('name','like','xlsx')]}
            self.file = False
        else:
            self.attachment_id = False
        return {'domain': domain}

    def _prepare_values_sale_order(self):
        return {
            'Order Reference':['SCT','name','Order Reference'],
            'commitment_date': ['Delivery Date','Ngày','commitment_date'], 
            'barcode': ['barcode','Mã KH'],
            'partner_id': ['Khách hàng','Customer/Name','partner_id','Customer'],
            'date_order': ['Order Date','Ngày báo giá','date_order'],
            'picking_policy': ['Shipping Policy','Chính sách vận chuyển','picking_policy'],
        }

    def _prepare_values_sale_line(self):
        return {
            'Order Reference':['SCT','name','Order Reference'],
            'barcode':['Product Barcode','Mã vạch','Barcode','barcode','Order Lines/Product/Barcode'],
            'default_code':['Mã sản phẩm','Product default Code','default_code','Order Lines/Product/Internal Reference'],
            'name':['Tên sản phẩm','name','Product Product','Product Name','Order Lines/Product/Name'],
            'product_uom_qty':['Số lượng','product_uom_qty','Order Lines/Quantity','Quantity'],
            'note':['Ghi chú','note'],
            'price_unit':['Đơn giá','Order Lines/Unit Price','price_unit','Unit Price'],
		    'commitment_date':['Commitment Date','Order Lines/Commitment Date','commitment_date','Commitment Date'],
            'sanluong':['Sản Lượng','Order Lines/Sản Lượng','sanluong','Sản Lượng'],
            'do':['Độ', 'Order Lines/Độ','do','Độ']
        }
        
    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains.
           Note: company_ids contains the ids of the activated companies
           by the user with the switch company menu. These companies are
           filtered and trusted.
        """
        # use an empty context for 'user' to make the domain evaluation
        # independent from the context
        return {
            'user': self.env.user.with_context({}),
            'time': time,
            'company_ids': self.env.companies.ids,
            'company_id': self.env.company.id,
        }
        

    def read_xls_book(self,file):
        book = xlrd.open_workbook(file_contents=base64.decodebytes(file))
        try:
            sheet_name = book.sheet_names()[0]
            sheet = book.sheet_by_name(sheet_name)
        except Exception as e:
            raise UserError(_(e))
        values_sheet = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            if all(str(e.value).strip() == '' for e in row):
                # skip all empty value in row.
                continue
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    dt = datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                            'row': rowx,
                            'col': colx,
                            'cell_value': xlrd.error_text_from_code.get(cell.value, _("unknown error code %s") % cell.value)
                        }
                    )
                else:
                    if '\n' in cell.value:
                        val = ''.join(cell.value.split('\n'))
                    else:
                        val = cell.value
                    values.append(val.strip())
            values_sheet.append(values)
        skip_header = True
        value_1=[]
        value_2=[]

        vali_sale_order = self._prepare_values_sale_order()
        vali_sale_line = self._prepare_values_sale_line()
        for row in values_sheet:
            value_sale_order = {}
            value_sale_line = {}
            if skip_header:
                skip_header = False
                continue
            val = dict(zip(values_sheet[0] , row ))
            if list(filter(lambda x: x in ['Tổng cộng:','Untaxed Amount','Total'],val.values())):
                continue
            for k, v in val.items():
                for k1, v1 in vali_sale_order.items():
                    if k in v1:
                        value_sale_order[k1] = v
                        break
            # merge_sale_line={}
            # for rec in vali_sale_line.values():
            #     merge_sale_line.update(rec) 
            for k_val, v_val in val.items():
                for k_line, v_line in vali_sale_line.items():
                    if k_val in v_line:
                        value_sale_line[k_line] = v_val
                        break
            value_1.append(value_sale_order)
            value_2.append(value_sale_line)
        sorte_order = sorted(value_1, key=itemgetter('Order Reference'))
        result_order = dict((k, list(g)[0]) for k, g in itertools.groupby(sorte_order, key=itemgetter('Order Reference')))

        sorte_line = sorted(value_2, key=itemgetter('Order Reference'))
        result_line = dict((k, list(g)) for k, g in itertools.groupby(sorte_line, key=itemgetter('Order Reference')))
        if self.import_type=='sale_order':
            result = {'sale_order':result_order,'sale_line':result_line}
        else: 
            result = {'sale_line':result_line}
        return result

    def create_sale_order(self,order):
        counter_so = 0
        so_val={}
        skipped_order_no = {}
        if 'Order Reference' in order:
            order.pop('Order Reference')
        obj_order = self.env['sale.order']
        for key,val in order.items():
            try:
                field = obj_order.fields_get(key).get(key)
                model_field = self.env[obj_order._name].fields_get(key).get(key).get('relation')
                if field.get('type') == 'many2one':
                    if self.env[model_field].fields_get('name'):
                        if field.get('domain'):
                            domain = [('name','=',val)] + safe_eval(field.get('domain'),self._eval_context())
                        else:
                            domain = [('name','=',val)] 
                        record = self.env[model_field].search(domain,limit=1)
                    else :
                        if field.get('domain'):
                            domain = [(key,'=',val)] + safe_eval(field.get('domain'),self._eval_context())
                        else:
                            domain = [(key,'=',val)] 
                        record = self.env[model_field].search(domain,limit=1)
                    if record:
                        so_val.update({key: record.id })
                    else:
                        if field.get('required'):
                            skipped_order_no[str(counter_so)] =_(" - No matching record found for"+key +":",+ val)
                            if val.strip() == '':
                                skipped_order_no[str(counter_so)] = _(" - Empty value"+"-"+ field.get('string'))
                            counter_so = counter_so + 1
                        else:
                            so_val.update({key: False })
                elif field.get('type') in ['many2many','one2many']:
                    continue
                elif field.get('type') =='selection':
                    so_val.update({key: list(filter(lambda x: x[-1] == 'As soon as possible', field.get('selection')))[0][0]})
                else:
                    so_val.update({key: val})
            except Exception as e:
                if skipped_order_no:
                    dic_msg = ''
                    if skipped_order_no:
                        dic_msg = dic_msg + "Errors (%s):" % str(len(skipped_order_no) + 1) # add 1 sourcecode error.
                        for k, v in skipped_order_no.items():
                            dic_msg = dic_msg + "\nRow. " + k + v
                    dic_msg = dic_msg + _("\nRow. " + str(counter_so) + " - SourceCodeError: " + ustr(e))
                    raise ValidationError(dic_msg) 
        if skipped_order_no:    
            counter_so += 1
            completed_records = (counter_so - len(skipped_order_no))
            result={'completed':completed_records,'skip':skipped_order_no}
        else:
            if not so_val.get('date_order'):
                so_val.update({'date_order': datetime.now()})
            elif not so_val.get('picking_policy'):
                policy = obj_order.fields_get('picking_policy')['picking_policy'].get('selection')
                for rec in policy:
                    so_val.update({'picking_policy': rec[0]})
                    break
            create_success = False
            try:
                sale_order=obj_order.create(so_val)
                create_success = True
            except Exception as e:
                skipped_order_no[str(counter_so)] = _("Can't create record : " + str(e))
                pass
            if create_success == True:
                counter_so += 1
                completed_records = (counter_so - len(skipped_order_no))
                result={'order':sale_order,'completed':completed_records,'skip':skipped_order_no}
            else:
                counter_so += 1
                completed_records = (counter_so - len(skipped_order_no))
                result={'completed':completed_records,'skip':skipped_order_no}
        return result

    def create_sale_line(self,line,order,counter_sol):
        skipped_line_no ={}
        sol_obj = self.env['sale.order.line']
        obj_product = self.env['product.product']
        list_line = list(filter(lambda x: x.pop('Order Reference'),line))
        for rec in list_line:
            sol_val = {}
            for key,val in rec.items():
                try:
                    field = obj_product.fields_get(key).get(key)
                    if field:
                        if field.get('type') in ['many2one','char']:
                            if key =='name':
                                # record = self.env[obj_product._name].search([('name','=',val)],limit=1)
                                continue
                            else:
                                record= self.env[obj_product._name].search([(key,'=',val)],limit=1)
                            if record:
                                sol_val.update({'product_id': record.id })
                            else:
                                skipped_line_no[str(counter_sol)] = _(" - No matching record found for"+key +":",+ val)
                                if val.strip() == '':
                                    skipped_line_no[str(counter_sol)] = _(" - Empty value"+"-"+ field.get('string'))
                                counter_sol = counter_sol + 1
                                break
                        elif field.get('type') in ['many2many','one2many']:
                            continue

                    field_sol = sol_obj.fields_get(key).get(key)
                    if key =='name':
                        continue
                    if field_sol:
                        if field_sol.get('type') =='selection':
                            sol_val.update({key: list(filter(lambda x: x[-1] == 'As soon as possible', field.get('selection')))[0][0]})
                        elif field_sol.get('type') == 'float':
                            sol_val.update({key: float(val) })
                        elif field_sol.get('type') in ['many2many','one2many']:
                            continue
                        else:
                            sol_val.update({key: val})
                except Exception as e:
                    if skipped_line_no:
                        dic_msg = ''
                        if skipped_line_no:
                            dic_msg = dic_msg + "Errors (%s):" % str(len(skipped_line_no) + 1) # add 1 sourcecode error.
                            for k, v in skipped_line_no.items():
                                dic_msg = dic_msg + "\nRow. " + k + v
                        dic_msg = dic_msg + _("\nRow. " + str(counter_sol) + " - SourceCodeError: " + ustr(e))
                        raise ValidationError(dic_msg)
            if sol_val.get('product_id'):
                sol_val.update({'order_id': order.id})
                sol_obj.create(sol_val)
                counter_sol+=1
        completed_records = (counter_sol - len(skipped_line_no))
        result={'completed':completed_records,'skip':skipped_line_no}
        return result
   
    def import_sale_order(self):
        values = []
        if not self.file and not self.is_select_file:
            raise UserError(_("Please, upload your excel file or download a sample file below."))
        elif self.import_type != 'export' and self.file:
            values = self.read_xls_book(self.file)
        elif self.is_select_file:
            if not self.attachment_id:
                raise UserError(_("Please, upload your excel file or download a sample file below."))
            else:
                values = self.read_xls_book(self.attachment_id.datas)
        if len(values) < 1:
            raise UserError(_("The file is empty."))
        order = values.get('sale_order')
        line = values.get('sale_line')
        counter_so =0
        counter_sol = 0
        skipped_line ={}
        skipped_order_no = []
        skipped_line_no = []
        value = order
        if self.import_type =='sale_line' or self._context.get('import_type') == 'sale_line':
            value = line
        for key in list(reversed(sorted(value.keys()))):
            try:
                # Create Sale Order
                if self.import_type =='sale_order':
                    result = self.create_sale_order(order[key])
                    counter_so += result.get('completed')
                    skipped_order_no.append(result.get('skip'))
                    if result.get('order'):
                        so_line=self.create_sale_line(line[key],result.get('order'),counter_sol)
                        if not so_line:
                            skipped_line[str(counter_sol)] = _(" - loi roi ne:")
                            counter_sol = counter_sol + 1
                            skipped_line_no.append(skipped_line)
                            continue
                        counter_sol = so_line.get('completed')
                        skipped_line_no.append(so_line.get('skip'))
                # Create Sale Order Line
                else:
                    if self._context.get('order'):
                        order_id = self.env['sale.order'].browse(int(self._context.get('order')))
                    else:
                        order_id = self.sale_order_id
                    result = self.create_sale_line(line[key],order_id,counter_sol)
                    counter_sol = result.get('completed')
                    skipped_line_no.append(result.get('skip'))
            except Exception as e:
                dic_msg = ''
                if skipped_line_no:
                    dic_msg = dic_msg + "Errors (%s):" % str(len(skipped_line_no) + 1)
                    for k, v in skipped_line_no.items():
                        dic_msg = dic_msg + "\nRow. " + k + v
                dic_msg = dic_msg + _("\nRow. "+ " - SourceCodeError: " + ustr(e))
                raise ValidationError(dic_msg)

        if counter_so > 1 or counter_sol > 1:
            skip_order = list(filter(lambda x : x!={},skipped_order_no))
            skip_line =list(filter(lambda x : x!={},skipped_line_no))
            if self.import_type=='sale_order':
                completed_records = (counter_so - len(skip_order))
                skip=skip_order +skip_line
                res = self.show_success_msg(
                    completed_records,skip)
            else:
                completed_records = (counter_sol - len(skip_line))
                res = self.show_success_msg(
                    completed_records, skip_line)
            return res

    def show_success_msg(self, counter, skipped_no):
        # open the new success message box
        view = self.env.ref('odb_base.wizard_message_popup')
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_no:
            dic_msg = dic_msg + "\nNote:"
        for rec in skipped_no:    
            for k, v in rec.items():
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

    def action_export_order(self):
        if self.sale_order_ids:
            order = self.sale_order_ids.ids
        else:
            order=[self.env.context.get('order')]
        data = {
            "ids": order,
        }
        return self.env["report.odb_sale_management.get_list_sale_order"].get_action(data)
