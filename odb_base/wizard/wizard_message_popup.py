# -*- coding: utf-8 -*-
from odoo import fields, models

class WizardMessagePopup(models.TransientModel):
    _name = "wizard.message.popup"
    _description = "Message wizard to display warnings, alert ,success messages"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
