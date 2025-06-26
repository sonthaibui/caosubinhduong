from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
import math, calendar
        
class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    diachi = fields.Selection([
        ('0', 'Không Xét'),('500000', '10-30km'), ('1000000', '>30km trong tỉnh'), ('1500000', '>30km ngoài tỉnh'), ('2000000', '>30km ngoài tỉnh khó khăn')
    ], string='Địa chỉ', default='0', required=True)