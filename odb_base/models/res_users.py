# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command

class Users(models.Model):
    _inherit = 'res.users'
    
    def action_reset_access(self):
        self.env['ir.model.access'].call_cache_clearing_methods()
        for user in self.with_context(active_test=False):
            user.write({'groups_id': [(5, 0, 0)] + [(4, self.env.ref('base.group_user').id)]})
        return True
    
    def action_setup_access(self):
        action = self.env["ir.actions.actions"]._for_xml_id("odb_base.action_setup_access")
        action['context'] = {'hide_specified_user': True, 'active_ids': self.ids}
        return action
    
