from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import _, fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    encrypt_password = fields.Char('Encrypt Password')

    def _render_qweb_pdf(self, res_ids=None, data=None):
        document, ttype = super(IrActionsReport, self)._render_qweb_pdf(
            res_ids=res_ids, data=data
        )
        if res_ids:
            if isinstance(res_ids, int):
                res_ids = [res_ids]
            password = self._get_pdf_password(res_ids[:1])
            document = self._encrypt_pdf(document, password)
        return document, ttype

    def _get_pdf_password(self, res_id):
        encrypt_password = self.encrypt_password
        return encrypt_password

    def _encrypt_pdf(self, data, password):
        if not password:
            return data
        output_pdf = PdfFileWriter()
        in_buff = BytesIO(data)
        pdf = PdfFileReader(in_buff)
        output_pdf.appendPagesFromReader(pdf)
        output_pdf.encrypt(password)
        buff = BytesIO()
        output_pdf.write(buff)
        return buff.getvalue()

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {"encrypt"}