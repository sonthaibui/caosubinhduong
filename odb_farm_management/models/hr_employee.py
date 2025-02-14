from odoo import fields, models, api 

class LandHrEmployee(models.Model):
    _inherit = 'hr.employee'

    farmer_team_id = fields.Many2one('farmer.team', string='Farmer Team')
    farm_zone_id = fields.Many2many('farm.zone', string='Land')