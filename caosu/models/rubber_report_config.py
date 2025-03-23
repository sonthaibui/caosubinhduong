# In a new file: models/rubber_config.py
from odoo import models, fields, api

class RubberDepartmentConfig(models.Model):
    _name = 'rubber.department.config'
    _description = 'Rubber Department Configuration'
    
    # Add constraint to ensure only one active record
    _sql_constraints = [
        ('single_active_config', 'UNIQUE(active)', 
         'Only one active configuration is allowed. Please deactivate the existing one first.')
    ]
    
    name = fields.Char(default="Department Configuration", readonly=True)
    department_ids = fields.Many2many('hr.department', string='Available Departments', 
                                      help="Departments that will be available in Rubber Reports")
    active = fields.Boolean(default=True)
    
    @api.model
    def get_departments(self):
        """Get the configured departments or fallback to defaults"""
        config = self.search([('active', '=', True)], limit=1)
        if config and config.department_ids:
            return config.department_ids.sorted(key=lambda d: d.name)
        
        # Fallback to hardcoded IDs if no configuration exists
        default_dept_ids = [1, 2, 3, 37, 72, 73, 76, 77, 83]
        return self.env['hr.department'].browse(default_dept_ids).sorted(key=lambda d: d.name)
    
    # Add this method to create a default config if none exists
    @api.model
    def create_default_config(self):
        """Create default configuration if none exists"""
        if not self.search_count([]):
            # Create with default departments
            default_dept_ids = [1, 2, 3, 37, 72, 73, 76, 77, 83]
            departments = self.env['hr.department'].browse(default_dept_ids)
            self.create({
                'name': 'Default Department Configuration',
                'department_ids': [(6, 0, departments.ids)],
                'active': True
            })