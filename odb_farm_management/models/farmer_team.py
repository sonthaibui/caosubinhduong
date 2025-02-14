from odoo import fields, models, api 

class LandPlanTeam(models.Model):
    _name = 'farmer.team'

    name = fields.Char('Name', required=True)
    emp_ids = fields.One2many('hr.employee', 'farmer_team_id', string='Employee')
    farm_zone_id = fields.Many2one('farm.zone', string='Small Land')
