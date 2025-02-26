# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SalePaymentMethod(models.Model):
    _name = 'sale.payment.method'
    _description = 'Sale Order Payment Method'

# Có thể thêm các field liên quan đến kế toán như journal_id để ghi nhận cách thức thanh toán sẽ ghi nhận ở sổ nhật ký nào

    name = fields.Char(string="Name", copy=False)