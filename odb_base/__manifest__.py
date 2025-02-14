# -*- coding: utf-8 -*-
{
    'name': 'General Base',
    'version': '1.0.2',
    'description': '''
        - Improve Sequence (ir.sequence)
        - Development Roles, Access Rights (res.role)
        - Improve Lang (res.lang)
        - Tools by python for Developer
    ''',
    'category': 'Hidden',
    'author': 'DuyBQ',
    'author_email': '<duybq86@gmail.com>',
    'website': 'https://www.odoobase.com/', 
    'depends': ['base_setup'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        
        'wizard/setup_access_views.xml',
        'wizard/wizard_message_popup.xml',
        'views/ir_module_module_view.xml',
        'views/ir_sequence_views.xml',
        'views/res_role_views.xml',
        'views/res_groups_views.xml',
        'views/res_users_view.xml',
        'views/res_partner.xml',
        'views/menu_view.xml',
            ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,

}
