# -*- coding: utf-8 -*-
{
    'name': 'Cash Book, Day Book, Bank Book Financial Reports',
    'version': '1.0.1',
    'category': 'Accounting',
    'summary': 'Cash Book, Day Book and Bank Book Report For Odoo 15',
    'description': 'Cash Book, Day Book and Bank Book Report For Odoo 15',
    'sequence': '10',
    'author': 'DuyBQ',
    'website': 'https://www.odoobase.com/',
    'depends': [
        'account',
        'odb_account_accountant',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',

        'wizard/account_daybook_report.xml',
        'wizard/account_cashbook_report.xml',
        'wizard/account_bankbook_report.xml',

        'report/reports.xml',
        'report/report_daybook.xml',
        'report/report_cashbook.xml',
        'report/report_bankbook.xml',

        'views/menu_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
