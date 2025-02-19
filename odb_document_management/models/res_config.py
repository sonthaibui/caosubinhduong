from odoo import fields, models


class DocumentConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_attachment_indexation = fields.Boolean(
        "Attachments List and Document Indexation",
        help="Document indexation, full text search of attachements.\n"
        "- This installs the module attachment_indexation.",
    )

    group_ir_attachment_user = fields.Boolean(
        string="Central access to Documents",
        help="When you set this field all users will be able to manage "
        "attachments centrally, from the Document/Documents menu.",
        implied_group="odb_document_management.group_ir_attachment_user",
    )

    module_document_page = fields.Boolean(
        "Manage document pages (Knowledge)",
        help="Provide document page and category as a knowledge.\n"
        "- This installs the module document_page.",
    )

    module_document_page_approval = fields.Boolean(
        "Manage documents approval",
        help="Add workflow on documents per category.\n"
        "- This installs the module document_page_approval.",
    )

    module_cmis_read = fields.Boolean(
        "Attach files from an external DMS into Odoo",
        help="Connect Odoo with a CMIS compatible server to attach files\n"
        "to an Odoo record.\n"
        "- This installs the module cmis_read.",
    )

    module_cmis_write = fields.Boolean(
        "Store attachments in an external DMS instead of the Odoo Filestore",
        help="Connect Odoo with a CMIS compatible server to store files.\n"
        "- This installs the module cmis_write.",
    )
    custom_header_footer_document = fields.Boolean(
        "Custom Header & Footer",
        help="Allow custom header and footer that is defined in res.company.\n",
        default=False
    )

    def set_values(self):
        super(DocumentConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param("odb_document_management.custom_header_footer_document", (self.custom_header_footer_document or False))

    
    def get_values(self):
        res = super(DocumentConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            custom_header_footer_document = params.get_param('odb_document_management.custom_header_footer_document', default=False),
        )
        return res


