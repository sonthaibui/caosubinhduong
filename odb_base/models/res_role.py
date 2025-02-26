# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _

from odoo.osv import expression
from odoo.exceptions import UserError
    
class Role(models.Model):
    _name = "res.role"
    _description = "Roles, Access Rights"
    _order = 'category_id'
    
    @api.model
    def _get_default_category(self):
        category = self.env.ref('base.module_category_extra', raise_if_not_found=False)
        return category
    
    name = fields.Char(string='Role, Access', required=True, translate=True, default='/')
    full_name = fields.Char(compute='_compute_full_name', string='Group Name', search='_search_full_name')
    
    description = fields.Text(translate=True)
    
    group_ids = fields.Many2many('res.groups', 
        'res_groups_role_rel', 'role_id', 'group_id', string='Groups', required=True, ondelete='restrict')
    category_id = fields.Many2one('ir.module.category', string='Application', index=True, ondelete='cascade', default=_get_default_category)
    
    @api.depends('category_id.name', 'name')
    def _compute_full_name(self):
        # Important: value must be stored in environment of group, not group1!
        for group, group1 in zip(self, self.sudo()):
            if group1.category_id:
                group.full_name = '%s / %s' % (group1.category_id.name, group1.name)
            else:
                group.full_name = group1.name
                
    def name_get(self):
        result = []
        for role in self:
            result.append((role.id, role.full_name))
        return result

    def _search_full_name(self, operator, operand):
        lst = True
        if isinstance(operand, bool):
            domains = [[('name', operator, operand)], [('category_id.name', operator, operand)]]
            if operator in expression.NEGATIVE_TERM_OPERATORS == (not operand):
                return expression.AND(domains)
            else:
                return expression.OR(domains)
        if isinstance(operand, str):
            lst = False
            operand = [operand]
        where = []
        for group in operand:
            values = [v for v in group.split('/') if v]
            group_name = values.pop().strip()
            category_name = values and '/'.join(values).strip() or group_name
            group_domain = [('name', operator, lst and [group_name] or group_name)]
            category_domain = [('category_id.name', operator, lst and [category_name] or category_name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS and not values:
                category_domain = expression.OR([category_domain, [('category_id', '=', False)]])
            if (operator in expression.NEGATIVE_TERM_OPERATORS) == (not values):
                sub_where = expression.AND([group_domain, category_domain])
            else:
                sub_where = expression.OR([group_domain, category_domain])
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                where = expression.AND([where, sub_where])
            else:
                where = expression.OR([where, sub_where])
        return where
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        name = name and name.strip()
        domain = []
        if name:
            domain = ['|',('full_name',operator, name),('category_id', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
    
    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        default_name = chosen_name or _('%s (copy)', self.name)
        default = dict(default or {}, name=default_name)
        return super().copy(default)

    
