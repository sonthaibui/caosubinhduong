from odoo import fields, models
class ProjectTask(models.Model):
    _inherit = 'project.task'      
    
    project_stage_id = fields.Many2one(
        'project.project.stage',  # Assuming the stage model is 'project.project.stage'
        string='Project Stage',
        related='project_id.stage_id',
        store=True,  # Store the value in the database for grouping
    )   