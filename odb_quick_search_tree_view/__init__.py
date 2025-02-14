# -*- coding: utf-8 -*-
from . import model
from . import controllers
from odoo.api import Environment, SUPERUSER_ID


def post_install_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    ks_user_data = {"users": [(4, user_id.id) for user_id in (env['res.users'].search([]))]}
    group_modify_view = env.ref('odb_quick_search_tree_view.group_modify_view')
    group_modify_view.write(ks_user_data)

    group_dynamic_list = env.ref('odb_quick_search_tree_view.group_dynamic_list')
    group_dynamic_list.write(ks_user_data)

    group_advance_search = env.ref('odb_quick_search_tree_view.group_advance_search')
    group_advance_search.write(ks_user_data)

def uninstall_hook(cr, registry):
    cr.execute(
        '''DELETE FROM ir_config_parameter WHERE (key LIKE '%serial_number%') OR (key LIKE '%ks_list_view_field_mode%') 
            OR (key LIKE '%ks_header_color_field_change%') OR (key LIKE '%toggle_color_field_change%') '''
    )

