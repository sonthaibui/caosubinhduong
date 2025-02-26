from odoo import fields, models, api 
from odoo.exceptions import ValidationError

class LandProductQuality(models.Model):
    _name = 'farm.produce.quality'
    _description = 'Land Product Quality'

    name = fields.Char('Quality', required=True)
    notes = fields.Text('Internal Notes')


