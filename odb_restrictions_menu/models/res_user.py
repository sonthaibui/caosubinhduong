# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HideMenuUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        """
        Else the menu will be still hidden even after removing from the list
        """
        self.clear_caches()
        return super(HideMenuUser, self).create(vals)

    def write(self, vals):
        """
        Else the menu will be still hidden even after removing from the list
        """
        res = super(HideMenuUser, self).write(vals)
        for menu in self.hide_menu_ids:
            menu.write({
                'restrict_user_ids': [(4, self.id)]
            })
        self.clear_caches()
        return res

    def _get_is_admin(self):
        """
        The Hide specific menu tab will be hidden for the Admin user form.
        Else once the menu is hidden, it will be difficult to re-enable it.
        """
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True

    hide_menu_ids = fields.Many2many('ir.ui.menu', string="Menu", store=True,
                                     help='Select menu items that needs to be '
                                          'hidden to this user ')
    is_admin = fields.Boolean(compute=_get_is_admin)


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'

    restrict_user_ids = fields.Many2many('res.users')
