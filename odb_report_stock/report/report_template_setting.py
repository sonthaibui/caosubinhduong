from odoo import _, api, fields, models

class TemplateSettings(models.Model):
    _inherit = "report.template.settings"

    def _get_default_picking(self):
        return self.env['ir.ui.view'].search([('key', '=', 'odb_report_stock.stock_template_0'),('type', '=', 'qweb')],order='key asc',limit=1)

    def _get_default_delivery(self):
        return self.env['ir.ui.view'].search([('key', '=', 'odb_report_stock.stock_delivery_template_0'),('type', '=', 'qweb')],order='key asc',limit=1)

    def _get_default_adjusment(self):
        return self.env['ir.ui.view'].search([('key', '=', 'odb_report_stock.report_adj_template_0'),('type', '=', 'qweb')],order='key asc',limit=1)

    def _get_default_stock_picking_batch(self):
        return self.env['ir.ui.view'].search([('key', '=', 'odb_report_stock.stock_picking_batch_template_0'),('type', '=', 'qweb')],order='key asc',limit=1)


    template_pk = fields.Many2one(
        string='Stock Picking Template',
        comodel_name='ir.ui.view',
        domain ="[('type', '=', 'qweb'), ('key', 'like', 'odb_report_stock.stock_template\_%')]",
        default= _get_default_picking
    )

    template_delivery = fields.Many2one(
        string='Stock Picking Delivery Template',
        comodel_name='ir.ui.view',
        domain ="[('type', '=', 'qweb'), ('key', 'like', 'odb_report_stock.stock_delivery_template\_%')]",
        default= _get_default_delivery
    )

    template_adj = fields.Many2one(
        string='Stock Inventory Adjusment Template',
        comodel_name='ir.ui.view',
        domain ="[('type', '=', 'qweb'), ('key', 'like', 'odb_report_stock.report_adj_template\_%')]",
        default= _get_default_adjusment
    )

    template_stock_picking_batch = fields.Many2one(
        string='Template Stock Picking Batch',
        comodel_name='ir.ui.view',
        domain ="[('type', '=', 'qweb'), ('key', 'like', 'odb_report_stock.stock_picking_batch_template\_%')]",
        default= _get_default_stock_picking_batch
    )