# -*- coding: utf-8 -*-
{
    'name': 'Account Journal Restrictions',
    'summary': '''Restrict users to certain journals''',
    'description': '''Restrict users to certain journals.''',
    'author': 'DuyBQ',
    'website': 'https://www.odoobase.com/',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'version': '1.0.1',
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'depends': [
        'account'
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir_rule.xml',

        'views/res_users.xml',
    ],
    'images': [
    ],
}
