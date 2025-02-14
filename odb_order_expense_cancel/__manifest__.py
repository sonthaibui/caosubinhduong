# -*- coding: utf-8 -*-
{
    'name' : 'Expenses Cancel',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ Expenses Cancel""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'hr_expense',
    ],
    'data': [
        'security/hr_security.xml',
        'data/data.xml',

        'views/hr_config_settings.xml',
        'views/hr_config_settings.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
