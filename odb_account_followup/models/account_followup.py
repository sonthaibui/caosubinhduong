# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountFollowup(models.Model):
    _name = 'account.followup'
    _description = 'Account Follow-up'
    _rec_name = 'name'

    name = fields.Char(string="Name", related='company_id.name', readonly=True)
    followup_line_ids = fields.One2many(
        'followup.line', 'followup_id', 'Follow-up', copy=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, default=lambda self: self.env.company)

    _sql_constraints = [('company_uniq', 'unique(company_id)',
                         'Only one follow-up per company is allowed')] 
