from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountVoucherWizard(models.TransientModel):
    _name = "account.voucher.wizard"
    _description = "Account Voucher Wizard"