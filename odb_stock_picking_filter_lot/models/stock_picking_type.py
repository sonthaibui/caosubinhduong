from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_filter_lots = fields.Boolean(
        "Use only available lots",
        default=True,
        help="If this is checked, only lots available in source location \
            would be displayed in drop down list for selecting lot.",
    )
