from odoo import models, fields, api 

class JobOperation(models.Model):
    _name = 'farm.job.operation'

    name = fields.Char('Job Operation', required=True)
    team_id = fields.Many2one('farmer.team', string='Team')
    quantity = fields.Integer('Quantity')
    member_ids = fields.Many2many('hr.employee', 'farm_job_operation_hr_employee_ref', string='Members', domain="[('farmer_team_id', '=', team_id)]")
    state = fields.Selection([
        ('pending', 'Pending'),     
        ('work', 'Work'),
        ('done', 'Done')],
        'State', default="pending")
    quality_id = fields.Many2one('farm.produce.quality', string='Quality')