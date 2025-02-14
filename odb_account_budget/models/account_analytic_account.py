# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    budget_line = fields.One2many('budget.lines', 'analytic_account_id', 'Budget Lines')
