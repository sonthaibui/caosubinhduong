# -*- coding: utf-8 -*-
from odoo import api, models,_


#  stock Adjustments
class ReportStockAdj(models.AbstractModel):
    _name = 'report.odb_report_stock.report_stock_picking_batch'
    _description = 'Report Account Report'
    
    def _get_report_values(self, docids, data=None):
        adj_obj = self.env['stock.picking.batch'].browse(docids)
        user = self.env["res.users"].browse(self._uid)
        company_data = user.company_id
        data = {
            'sale_header_footer': user.company_id.sale_header_footer,
            'primary_color': company_data.primary_color,
            'secondary_color': company_data.secondary_color,
            'sale_font_color': company_data.sale_font_color
        }
        docargs = {
            'doc_ids': docids,
            'doc_model': 'stock.inventory',
            'docs': adj_obj,
            'data': data,
            'doc': user,
        }
        return docargs
