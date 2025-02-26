# -*- coding: utf-8 -*-
{
    'name': 'Restrictions user of Menu',
    'version': '1.0.1',
    'summary': 'Restrictions user of Menu',
    'description': 'Restrictions user of Menu',
    'category': 'Tools',
    'author': 'DuyBQ',
    'website': "https://www.odoobase.com",
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['base'],
    'data': [
        'views/res_users.xml',
        'security/security.xml'
    ],

}
