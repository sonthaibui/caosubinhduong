from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from datetime import timedelta

class LandStage(models.Model):
    _name = 'farm.stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Land Pipe')
    done = fields.Boolean('Request Done')
