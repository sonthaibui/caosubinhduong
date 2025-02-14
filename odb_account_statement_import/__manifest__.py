# -*- encoding: utf-8 -*-
{
    'name': 'Account Statement Import',
    'version': '1.0.1',
    'category': 'Accounting',
    'depends': [
        'odb_base',
        'account',
        'odb_account_accountant',
    ],
    'website': 'https://www.odoobase.com/',
    'author': 'DuyBQ',
    'description': """Generic Wizard to Import Statements and Bank Statements.
(This module does include any CSV and XLSX type import format.)""",
    'data': [
        'security/ir.model.access.csv',

        'wizard/account_bank_statement_import_journal_creation.xml',

        'views/ir_module_module_views.xml',
        'views/account_bank_statement_import_view.xml',
        'views/account_journal_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'demo/partner_bank.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
