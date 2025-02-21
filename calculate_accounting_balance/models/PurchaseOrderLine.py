import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sanluong = fields.Float(string='Sản Lượng')
    do = fields.Float(string='Độ')

    @api.onchange('sanluong', 'do')
    def onchange_sanluong_do(self):
        self.product_qty = self.sanluong * (self.do / 100)