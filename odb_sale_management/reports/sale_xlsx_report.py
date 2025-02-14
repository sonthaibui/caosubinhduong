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
    _name = "report.odb_sale_management.get_list_sale_order"
    _description = "Report Sale Order"
    _inherit = "report.report_xlsx.abstract"


    def get_action(self, data):
        module = __name__.split("addons.")[1].split(".")[0]
        report_name = "{}.get_list_sale_order".format(module)
        report_file = 'List Order and Order Line'
        return {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "context": dict(self.env.context),
            "data": dict(data=data,report_file=report_file),
            }


    def generate_xlsx_report(self, workbook, data, obj):
        workbook.set_properties({"comments": "Created with Python and XlsxWriter from Odoo"})
        sale_object = self.env['sale.order'].browse(data.get('data').get('ids')) or obj
        bold = workbook.add_format({"bold": True})
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )
        sheet = workbook.add_worksheet(_("Generate Order"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 30)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 40)
        sheet.set_column(8, 8, 30)
        sheet.set_column(9, 9, 35)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)
        sheet.set_column(14, 14, 20)


        sheet_title = [
            _("Order Reference"),
            _("Customer"),
            _("Order Date"),
            _("Delivery Date"),
            # _("Seq"),
            _("Product Barcode"),
            _("Product default Code"),
            _("Product Name"),
            _("Product Attribute"),
            _("Description"),
            _("Quantity"),
            _("UoM"),
            _("Unit Price"),
            _("Taxes (%)"),
            _("Sub Total"),
        ]
        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(0, 0, sheet_title, title_style)
        sheet.freeze_panes(1, 1)
        row = 1
        seq=1
        for rec in sale_object.mapped('order_line'):
            col = 0
            sheet.write(row, col, str(rec.order_id.name))
            col +=1
            sheet.write(row, col, str(rec.order_id.partner_id.name))
            col +=1
            sheet.write(row, col, str(rec.order_id.date_order))
            col +=1
            sheet.write(row, col, str(rec.order_id.commitment_date))
            col +=1
            # sheet.write(row, col, str(seq))
            # col +=1
            sheet.write(row, col, rec.product_id.barcode if rec.product_id.barcode else '')
            col +=1
            sheet.write(row, col, rec.product_id.default_code if rec.product_id.default_code else '')
            col +=1
            sheet.write(row, col, rec.product_id.name)
            col +=1
            sheet.write(row, col, ','.join([line.product_attribute_value_id.display_name for line in rec.product_id.product_template_attribute_value_ids]))
            col +=1
            sheet.write(row, col, rec.name or "")
            col +=1
            sheet.write(row, col, rec.product_uom_qty)
            col +=1
            sheet.write(row, col, rec.product_uom.name)
            col +=1
            sheet.write(row, col, rec.price_unit)
            col +=1
            sheet.write(row, col, rec.tax_id[0].amount if rec.tax_id else "")
            col +=1
            sheet.write(row, col, rec.price_subtotal)
            row+=1
            seq+=1