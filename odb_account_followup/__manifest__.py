# -*- coding: utf-8 -*-
{
    'name': 'Customer Follow Up Management',
    'version': '1.0.1',
    'category': 'Accounting',
    'description': """Customer FollowUp Management""",
    'summary': """Customer FollowUp Management""",
    'author': 'DuyBQ',
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': [
        'account',
        'mail',
        'odb_account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        'data/data.xml',
        'data/mail_template.xml',

        'wizard/followup_print_view.xml',
        'wizard/followup_results_view.xml',

        'report/followup_stat.xml',

        'views/account_followup_line_views.xml',
        'views/account_followup_views.xml',
        'views/account_move_line.xml',
        'views/res_partners.xml',
        'views/report_followup.xml',
        'views/reports.xml',
        'views/followup_stat_by_partner.xml',
        'views/menu_views.xml',
    ],
    'demo': ['demo/demo.xml'],
}
