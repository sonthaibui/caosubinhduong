# -*- coding: utf-8 -*-
{
    'name': 'Stock Managerment',
    'summary': '''
        ''',
        'description': ''' ''',
    'category': 'Warehouse',
    'version': '1.0.1',
    'website': 'https://www.odoobase.com/',
    'author': 'Thinh.NV',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['stock'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'wizard/wizard_change_location.xml',
        'wizard/abstract_inventory_backdate_wizard_views.xml',
        
        'views/stock_picking_view.xml',
        'views/stock_move_view.xml',
        'views/stock_location_view.xml',
        'views/menu_views.xml',
    ],

}
