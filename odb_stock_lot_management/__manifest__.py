# -*- coding: utf-8 -*-
{
    'name': 'Lot/Seria Number Management',
    'summary': '''
        Lot/Seria Number Management
    ''',
    'description': '''
        Lot/Seria Number Management
    ''',
    'category': 'Warehouse',
    'version': '1.0.1',
    'website':  'https://www.odoobase.com/',
    'author': 'DuyBQ',
    'license': 'OEEL-1',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_move.xml',
    ],
}
