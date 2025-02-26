# -*- coding: utf-8 -*-
{
    'name' : 'Invoices Cancel',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ All Cancel all related order""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'account',
    ],
    'data': [
        'views/invoice.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
