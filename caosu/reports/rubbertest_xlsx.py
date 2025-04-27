from odoo import models
import logging

_logger = logging.getLogger(__name__)

class RubberTestXlsx(models.AbstractModel):
    _name = 'report.caosu.rubbertest_report_xlsx'  # Change this name
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Rubber Test XLSX Report'

    def create_xlsx_report(self, docids, data):
        workbook = self.get_workbook_options()
        worksheet = workbook.add_worksheet('Rubber Test Report')
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#f8f9fa',
            'border': 1
        })

        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Write headers
        headers = ['Cây', 'Vanh', 'Mũ Nước', 'Mũ Chén', 'Mũ Dây', 'Mũ Đông', 'Mũ Tạp', 'Ghi chú']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Get report data
        records = self.env['rubber.test'].browse(docids)
        report_data = records.get_report_data()

        # Write data
        for row_idx, record in enumerate(report_data, 1):
            for col_idx, value in enumerate(record):
                worksheet.write(row_idx, col_idx, value, cell_format)

        # Set column widths
        worksheet.set_column('A:H', 15)

        return workbook