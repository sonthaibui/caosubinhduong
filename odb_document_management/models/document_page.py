from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class DocumentPage(models.Model):
    """This class is use to manage Document."""

    _name = "document.page"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Document Page"
    _order = "name"

    _HTML_WIDGET_DEFAULT_VALUE = "<p><br></p>"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char("Title", required=True, translate=True)
    type = fields.Selection([("content", "Content"), ("category", "Category")], "Type", help="Page type", default="content",)
    parent_id = fields.Many2one("document.page", "Category", domain=[
                                ("type", "=", "category")])
    child_ids = fields.One2many("document.page", "parent_id", "Children")
    content = fields.Text("Content", compute="_compute_content", inverse="_inverse_content", search="_search_content", translate=True)
    draft_name = fields.Char(string="Name", help="Name for the changes made", related="history_head.name", readonly=False,)
    draft_summary = fields.Char(string="Summary", help="Describe the changes made", related="history_head.summary", readonly=False,)

    template = fields.Html(
        "Template",
        help="Template that will be used as a content template "
        "for all new page of this category.",
        translate=True,
    )
    history_head = fields.Many2one("document.page.history", "HEAD", compute="_compute_history_head", store=True, auto_join=True,)
    history_ids = fields.One2many("document.page.history", "page_id", "History", readonly=True,)
    menu_id = fields.Many2one("ir.ui.menu", "Menu", readonly=True)
    content_date = fields.Datetime("Last Contribution Date", related="history_head.create_date", store=True, index=True, readonly=True,)
    content_uid = fields.Many2one("res.users", "Last Contributor", related="history_head.create_uid",
        store=True, index=True, readonly=True,)
    company_id = fields.Many2one("res.company", "Company", help="If set, page is accessible only from this company",
        index=True, ondelete="cascade", default=lambda self: self.env.company,)
    backend_url = fields.Char(string="Backend URL", help="Use it to link resources univocally",
        compute="_compute_backend_url",)
    group_ids = fields.Many2many("res.groups", store=True, relation="document_page_direct_group",
        column1="document_page_id", column2="group_id", compute="_compute_group_ids",)
    direct_group_ids = fields.Many2many("res.groups", string="Visible to", help="Set the groups that can view this category and its childs",
        relation="document_page_group", column1="document_page_id", column2="group_id",)
    is_custom_header_footer = fields.Boolean(string='Custom head and footer', compute='_compute_custom_from_setting')
    color = fields.Integer(string='Color Index', help="Color")

    def _compute_custom_from_setting(self):
        settings = self.env['ir.config_parameter'].sudo().get_param('odb_document_management.custom_header_footer_document') or False
        for rec in self:
            rec.is_custom_header_footer = settings

    @api.model
    def default_get(self, fields):
        default_values = super(DocumentPage, self).default_get(fields)
        line_ids = self.env.context.get('line_ids', False)
        if line_ids:
            lines = self.env['model'].resolve_2many_commands(
                'line_ids', line_ids)
            lines.sort(key=lambda x: x.get('sequence'))
            if lines:
                sequence = lines[-1]['sequence'] + 10
            else:
                sequence = 10
            default_values.update({'sequence': sequence})
        return default_values

    @api.depends("direct_group_ids", "parent_id", "parent_id.group_ids")
    def _compute_group_ids(self):
        for record in self:
            groups = record.direct_group_ids
            if record.parent_id:
                groups |= record.parent_id.group_ids
            record.group_ids = groups

    @api.depends("menu_id", "parent_id.menu_id")
    def _compute_backend_url(self):
        tmpl = "/web#id={}&model=document.page&view_type=form"
        for rec in self:
            url = tmpl.format(rec.id)
            # retrieve action
            action = None
            parent = rec
            while not action and parent:
                action = parent.menu_id.action
                parent = parent.parent_id
            if action:
                url += "&action={}".format(action.id)
            rec.backend_url = url

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive categories."))

    def _get_page_index(self, link=True):
        """Return the index of a document."""
        self.ensure_one()
        index = [
            "<li>" + subpage._get_page_index() + "</li>" for subpage in self.child_ids
        ]
        r = ""
        if link:
            r = '<a href="{}">{}</a>'.format(self.backend_url, self.name)
        if index:
            r += "<ul>" + "".join(index) + "</ul>"
        return r

    @api.depends("history_head")
    def _compute_content(self):
        for rec in self:
            if rec.type == "category":
                rec.content = rec._get_page_index(link=False)
            else:
                if rec.history_head:
                    rec.content = rec.history_head.content
                else:
                    # html widget's default, so it doesn't trigger ghost save
                    rec.content = self._HTML_WIDGET_DEFAULT_VALUE

    def _inverse_content(self):
        for rec in self:
            if rec.type == "content" and rec.content != rec.history_head.content:
                rec._create_history(
                    {
                        "page_id": rec.id,
                        "name": rec.draft_name,
                        "summary": rec.draft_summary,
                        "content": rec.content,
                    }
                )

    def _create_history(self, vals):
        self.ensure_one()
        return self.env["document.page.history"].create(vals)

    def _search_content(self, operator, value):
        return [("history_head.content", operator, value)]

    @api.depends("history_ids")
    def _compute_history_head(self):
        for rec in self:
            if rec.history_ids:
                rec.history_head = rec.history_ids[0]
            else:
                rec.history_head = False

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """We Set it the right content to the new parent."""
        if (
            self.content in (False, self._HTML_WIDGET_DEFAULT_VALUE)
            and self.parent_id.type == "category"
        ):
            self.content = self.parent_id.template

    def unlink(self):
        menus = self.mapped("menu_id")
        res = super().unlink()
        menus.unlink()
        return res
