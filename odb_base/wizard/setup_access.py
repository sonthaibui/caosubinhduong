# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from itertools import chain

class SetupAccess(models.TransientModel):
    _name = "setup.access"
    _description = "Setup Access for Users"
    
    @api.model
    def _default_user_ids(self):
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        return [(4, user.id) for user in self.env['res.users'].browse(user_ids)]
    
    type = fields.Selection([('role', 'Roles, Access Rights'),('user', 'From User')], default='role')
    
    user_id = fields.Many2one('res.users', string='User', ondelete='set null')
    role_ids = fields.Many2many('res.role', string='Access Roles')
    
    specified_user_ids = fields.Many2many('res.users', string='Specified Users', default=_default_user_ids)
    
    def action_confirm(self):
        if self.type == 'user':
            gs = set(chain.from_iterable(self.sudo().user_id.groups_id))
        else:
            gs = set(chain.from_iterable(self.sudo().mapped('role_ids.group_ids')))
        for user in self.sudo().with_context(active_test=False).specified_user_ids:
            user.write({'groups_id': [(4, g.id) for g in gs]})
        return True
    
    def action_clean_group(self):
        self.sudo().specified_user_ids.action_clean_group()
        

    
