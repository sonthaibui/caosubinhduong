# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.exceptions import AccessError
from odoo.sql_db import TestCursor
from odoo.tools import config
from odoo.tools.misc import find_in_path
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from base64 import b64decode
from logging import getLogger
from PIL import Image
import io
from io import StringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.errors import PdfReadError

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.errors import PdfReadError  # pylint: disable=W0404
except ImportError:
    pass
try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
logger = getLogger(__name__)

Selection_Field = [
            ('template1', 'Professional Report'),
            ('template2', 'Retro Report'),
            ('template3', 'Fency Report'),
            ('template4', 'Classic Report'),
            ('template5', 'CNC Report'),
        ]
Selection_Label = [
            ('template1', 'Template 1'),
            ('template2', 'Template 2'),
            ('template3', 'Template 3'),
            ('template4', 'Template 4'),
        ]


class ResCompany(models.Model):
    _inherit = ['res.company']

    temp_selection = fields.Selection(Selection_Field, 'Template for Purchase, Sale, Invoice, Stock, Manufacturing', default='template2')
    add_watermark = fields.Boolean('Want Watermark?', default='False')
    add_signature = fields.Boolean('Want Signature?', default='False')
    watermark_selection = fields.Selection([('letter_head', 'Letter Head'), ('company_logo', 'Company Logo'), ('custom_name', 'Text')], 'Watermark Selection')
    custom_watermark_name = fields.Char('Watermark Name')
    add_product_image = fields.Boolean('Show Product Image in Report')
    sale_header_footer = fields.Char('Select Header & Footer Color')
    primary_color = fields.Char('Select Primary Color', default="#000000")
    secondary_color = fields.Char('Select Secondary Color', default="#FF6600")
    sale_font_color = fields.Char('Select Font Color', default="#FFFFFF")
    letter_head = fields.Binary(string='Letter Logo')
    signature_logo = fields.Binary(string='Signature Logo')
    show_price_label = fields.Boolean('Show Price on Labels')
    selection_label = fields.Selection(Selection_Label, 'Label Template', default='template2')

    header = fields.Html(string='Header')
    footer = fields.Html(string='Footer')
    df_style = fields.Many2one('report.template.settings', 'Default Style',
                               help="If no other report style is specified during the printing of document,\
                    this default style will be used")
    pdf_watermark = fields.Binary('Watermark PDF',
                                  help='Upload your company letterhead PDF or a PDF to form the background of your reports.\
                    This PDF will be used as the background of each an every page printed.')
    pdf_watermark_fname = fields.Char('Watermark Filename')
    pdf_last_page = fields.Binary('Last Pages PDF',
                                  help='Here you can upload a PDF document that contain some specific content \
                    such as product brochure,\n promotional content, advert, sale terms \
                    and Conditions,..etc.\n This document will be appended to the printed report')
    pdf_last_page_fname = fields.Char('Last Pages Filename')
    

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    
    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        user = self.env['res.users'].browse(self.env.uid)
        result = super(IrActionsReport, self)._post_pdf(
            save_in_attachment, pdf_content=pdf_content, res_ids=res_ids)
        if user.company_id.temp_selection == 'odoo_standard' or user.company_id.temp_selection == False or user.company_id.add_watermark == False:
            return result
        else:
            if user.company_id.add_watermark == True and user.company_id.watermark_selection == 'letter_head':
                result = super(IrActionsReport, self)._post_pdf(
                    save_in_attachment,
                    pdf_content=pdf_content,
                    res_ids=res_ids)
                user = self.env['res.users'].browse(self.env.uid)
                watermark = None
                if user.company_id.letter_head:
                    watermark = b64decode(user.company_id.letter_head)
                else:
                    if watermark:
                        watermark = b64decode(watermark)

                if not watermark:
                    return result

                pdf = PdfFileWriter()
                pdf_watermark = None
                watermark_streams = []
                try:
                    # pdf_watermark = PdfFileReader(StringIO(watermark))
                    pdf_watermark = io.BytesIO(watermark)
                    watermark_streams.append(pdf_watermark)
                    pdf_watermark = PdfFileReader(pdf_watermark)
                except PdfReadError:
                    # let's see if we can convert this with pillow
                    try:
                        image = Image.open(io.BytesIO(watermark))
                        pdf_buffer = io.BytesIO()
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        resolution = image.info.get(
                            'dpi', user.company_id.paperformat_id.dpi or 90)
                        if isinstance(resolution, tuple):
                            resolution = resolution[0]
                        image.save(pdf_buffer, 'pdf', resolution=resolution)
                        pdf_watermark = PdfFileReader(pdf_buffer)
                    except:
                        logger.exception(
                            'Failed************ to load watermark')

                if not pdf_watermark:
                    logger.error('No usable watermark found, got %s...',
                                 watermark[:100])
                    return result
                if pdf_watermark.numPages < 1:
                    logger.error(
                        'Your watermark pdf does not contain any pages')
                    return result
                if pdf_watermark.numPages > 1:
                    logger.debug(
                        'Your watermark pdf contains more than one page, '
                        'all but the first one will be ignored')

                for page in PdfFileReader(io.BytesIO(result)).pages:
                    watermark_page = pdf.addBlankPage(
                        page.mediaBox.getWidth(), page.mediaBox.getHeight())
                    watermark_page.mergePage(pdf_watermark.getPage(0))
                    watermark_page.mergePage(page)
                pdf_content = io.BytesIO()
                pdf.write(pdf_content)
                return pdf_content.getvalue()
            else:
                return result
