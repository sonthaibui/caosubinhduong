import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    kanban_state_id = fields.Many2one('kanban.state', string='Kanban State')