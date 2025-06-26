from odoo import models, fields

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    
    # Add all custom fields that you added to hr.employee
    # diachi = fields.Char(string="Địa chỉ")
    # Add any other custom fields you added to hr.employee