from odoo import models, fields, api

class RubbertestDepartmentConfig(models.Model):
    _name = 'rubbertest.department.config'
    _description = 'Rubber Test Department Configuration'
    
    name = fields.Char(string="Configuration Name", default="Department Configuration")
    department_ids = fields.Many2many('hr.department', 'rubbertest_dept_config_rel', 
                                     'config_id', 'department_id',
                                     string='Available Departments')
    active = fields.Boolean(default=True)
    
    @api.model
    def get_departments(self):
        """Get the configured departments or fallback to defaults"""
        config = self.search([('active', '=', True)], limit=1)
        if config and config.department_ids:
            return config.department_ids.sorted(key=lambda d: d.name)
        
        # Fallback to default departments
        default_dept_ids = [72, 76, 73, 77, 84, 37, 83]  # Your hardcoded department IDs
        return self.env['hr.department'].browse(default_dept_ids).sorted(key=lambda d: d.name)
    
    @api.model
    def create(self, vals):
        """Override create to handle single active record constraint"""
        if vals.get('active', True):
            # Deactivate other active records
            self.search([('active', '=', True)]).write({'active': False})
        return super(RubbertestDepartmentConfig, self).create(vals)
    
    def write(self, vals):
        """Override write to handle single active record constraint"""
        if vals.get('active', False):
            # Deactivate other active records
            self.search([('id', '!=', self.id), ('active', '=', True)]).write({'active': False})
        return super(RubbertestDepartmentConfig, self).write(vals)
    
    @api.model
    def ensure_default_config(self):
        """Create default configuration if none exists"""
        if not self.search_count([]):
            default_dept_ids = [72, 76, 73, 77, 84, 37, 83]  # Your hardcoded department IDs
            self.create({
                'name': 'Default Rubber Test Configuration',
                'department_ids': [(6, 0, default_dept_ids)],
                'active': True
            })
        return True