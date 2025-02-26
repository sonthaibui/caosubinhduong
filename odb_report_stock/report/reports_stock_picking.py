# -*- coding: utf-8 -*-
from odoo import api, models,_


class ReportStockReport(models.AbstractModel):
    _name = 'report.odb_report_stock.report_stok_picking'
    _description = 'Report Stock Report'
    
    def _get_report_values(self, docids, data=None):
        picking_obj = self.env['stock.picking'].browse(docids)
        user = self.env["res.users"].browse(self._uid)
        company_data = user.company_id

        report = self.env['ir.actions.report']._get_report_from_name('odb_report_stock.report_stok_picking')
        if picking_obj.picking_type_id.code == 'incoming':
            report['paperformat_id'] = self.env.ref('odb_report_stock.paperformat_stockpicking_receipts')
        elif picking_obj.picking_type_id.code == 'outgoing':
            report['paperformat_id'] = self.env.ref('odb_report_stock.paperformat_stockpicking')

        data = {
            'sale_header_footer': user.company_id.sale_header_footer,
            'primary_color': company_data.primary_color,
            'secondary_color': company_data.secondary_color,
            'sale_font_color': company_data.sale_font_color
        }
        docargs = {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': picking_obj,
            'data': data,
            'doc': user,
        }

        # if picking_obj.picking_type_id.code == 'incoming':
        #     purchase_ids = self.env['purchase.order'].search([('name', 'in', picking_obj.mapped('group_id.name'))])
        #     if purchase_ids:
        #         docargs.update({'po_isd': purchase_ids,})
        #         if purchase_ids.state == 'done':
        #             paid_invoice = purchase_ids.invoice_ids.filtered(lambda x: x.payment_state == 'paid')
        #             if paid_invoice:
        #                 paid_invoice = paid_invoice[:1]
        #                 docargs.update({'proforma_date': paid_invoice})
        return docargs
