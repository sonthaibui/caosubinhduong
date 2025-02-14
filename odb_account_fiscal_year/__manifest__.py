# -*- coding: utf-8 -*-
{
    'name': 'Accounting Fiscal Year & Lock Date',
    'version': '1.0.1',
    'category': 'Accounting',
    'summary': 'Accounting Fiscal Year & Lock Date',
    'description': 'Accounting Fiscal Year & Lock Date',
    'sequence': '1',
    'website': 'https://www.odoobase.com/',
    'author': 'DuyBQ',
    'depends': [
        'account',
        'odb_account_accountant',
    ],
    'excludes': [
        'account_accountant'
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',

        'wizard/account_lock_date.xml',

        'views/account_fiscal_year.xml',
        'views/res_config_settings.xml',
        'views/menu_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
