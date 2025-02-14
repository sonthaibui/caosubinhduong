# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountIncoterm(models.Model):
    _inherit = 'account.incoterms'

    
    description = fields.Html(string='Description')
    