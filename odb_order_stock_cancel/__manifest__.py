# -*- coding: utf-8 -*-
{
    'name' : 'Stock Cancel Order',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ All Cancel all related order""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'stock',
        ],
    'data': [
        'views/stock_picking.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
