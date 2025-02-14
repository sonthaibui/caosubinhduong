from odoo import models, fields, api, _


class FarmJobLine(models.Model):
    _name = 'farm.job.line'

    name = fields.Char('Name', required=True)
    notes = fields.Text('Internal Notes')