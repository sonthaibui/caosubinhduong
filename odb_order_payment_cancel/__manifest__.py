# -*- coding: utf-8 -*-
{
    'name' : 'Payment Order Cancel',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ All Cancel all related order""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'stock',
        'account_payment',
        ],
    'data': [
        'security/res_group.xml',
        # 'security/ir.model.access.csv',
        'views/account_payment.xml',
        'views/account_move.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
