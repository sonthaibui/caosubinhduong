# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if vals.get('name',False) in [False,'New']:
            vals.update({
                'name':self.env['ir.sequence'].next_by_code('sequence.purchase.order'),
            })
        return super(PurchaseOrder, self).create(vals)

    def button_confirm(self):
        for line in self.order_line:
            if line.product_id.detailed_type =='service':
                line.qty_received = line.product_qty
        return super(PurchaseOrder,self).button_confirm()


    # def _get_invoiced(self):
    #     res = super(PurchaseOrder,self)._get_invoiced()
    #     return res

    def action_rfq_send(self):
        res = super(PurchaseOrder, self).action_rfq_send()
        excel_template_id = self.env.ref('odb_purchase_management.get_list_purchase_order_xlsx').sudo()._render_xlsx(self.ids,[])
        data_record = base64.b64encode(excel_template_id[0])
        file_name = 'RFQ_' + self.name + '.xlsx'
        ir_values = {
            'name': file_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': file_name,
            'res_model': 'purchase.order',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        excel_attachment = self.env['ir.attachment'].create(ir_values)
        template = self.env['mail.template'].browse(res.get('context').get('default_template_id'))
        template.attachment_ids = False
        template.attachment_ids = [(4, excel_attachment.id)]
        return res


    def wizards_open_import_pol(self):
        view = self.env.ref('odb_purchase_management.wizard_import_purchase')
        context={'order':self.id,'import_type':'purchase_line'}
        return {
            'name': 'Wizards Import Purchase Order Line',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.import.purchase',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }


    