# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import date, timedelta
import logging
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

_logger = logging.getLogger(__name__)

                        
class PurchaseOrder(models.AbstractModel):
    _name = "report.odb_purchase_management.get_list_purchase_order"
    _description = "Report purchase Order"
    _inherit = "report.report_xlsx.abstract"


    def get_action(self, data):
        module = __name__.split("addons.")[1].split(".")[0]
        report_name = "{}.get_list_purchase_order".format(module)
        report_file = 'List Order and Order Line'
        return {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "context": dict(self.env.context),
            "data": dict(data=data,report_file=report_file),
            }


    def generate_xlsx_report(self, workbook, data, obj):
        purchase_object = self.env['purchase.order'].browse(data.get('data').get('ids')) or obj
        self.env['purchase.order'].browse(data.get('data').get('ids')[0])
        workbook.set_properties({"comments": "Created with Python and XlsxWriter from Odoo"})
        bold = workbook.add_format({"bold": True})
        # bgcolor = workbook.add_format({"bg_color":"#1e732c","bold": True})
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )
        sheet = workbook.add_worksheet(_("List Order"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 50)
        sheet.set_column(5, 5, 40)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 11, 20)
        sheet.set_column(12, 12, 20)
        sheet.set_column(13, 13, 20)
        sheet_title = [
            # _("Seq"),
            _("Order Reference"),
            _("Vendor"),
            _("Deliver To"),
            _("Product Barcode"),
            _("Product default Code"),
            _("Product Product"),
            _("Product Attribute"),
            _("Description"),
            _("Quantity"),
            _("UoM"),
            _("Unit Price"),
            _("Taxes (%)"),
            _("Sub Total"),
            _("Source Document"),
        ]
        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(0, 0, sheet_title, title_style)
        sheet.freeze_panes(1, 1)
        data_format2 = workbook.add_format({'bg_color': '#d3db2c',"bold": True,})
        row = 1
        seq=1
        for rec in purchase_object.mapped('order_line'):
            col = 0
            # sheet.write(row, col, str(seq))
            sheet.write(row, col, rec.order_id.name)
            col +=1
            sheet.write(row, col, rec.order_id.partner_id.name)
            col +=1
            sheet.write(row, col, rec.order_id.picking_type_id.name)
            col +=1
            sheet.write(row, col, rec.product_id.barcode if rec.product_id.barcode else '')
            col +=1
            sheet.write(row, col, rec.product_id.default_code if rec.product_id.default_code else '')
            col +=1
            sheet.write(row, col, rec.product_id.name)
            col +=1
            sheet.write(row, col, ', '.join([line.product_attribute_value_id.display_name for line in rec.product_id.product_template_attribute_value_ids]))
            col +=1
            sheet.write(row, col, rec.name or "")
            col +=1
            sheet.write(row, col, rec.product_qty)
            col +=1
            sheet.write(row, col, rec.product_uom.name)
            col +=1
            sheet.write(row, col, rec.price_unit)
            col +=1
            sheet.write(row, col, rec.taxes_id[0].amount if rec.taxes_id else "")
            col +=1
            sheet.write(row, col, rec.price_subtotal)
            col +=1
            # sheet.write(row, col, rec.order_id.origin if rec.order_id.origin else '')
            row+=1
            # seq+=1