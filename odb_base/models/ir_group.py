    # -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Groups(models.Model):
    _inherit = "res.groups"
    
    role_ids = fields.Many2many('res.role', 
        'res_groups_role_rel', 'group_id', 'role_id', string='Roles, Access Rights')    
    
    
    
