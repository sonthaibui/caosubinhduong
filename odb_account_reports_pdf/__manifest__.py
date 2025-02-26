# -*- coding: utf-8 -*-

{
    'name': 'Accounting Financial Reports',
    'description': 'Accounting Financial Reports',
    'summary': 'Accounting Financial Reports',
    'version': '1.0.1',
    'category': 'Accounting',
    'sequence': '1',
    'author': 'DuyBQ',
    'website': 'https://www.odoobase.com/',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',

        'data/ir_actions_report.xml',
        'data/cash_flow_data.xml',

        'report/report_financial.xml',
        'report/cash_flow_report.xml',
        'report/report_partner_ledger.xml',
        'report/report_general_ledger.xml',
        'report/report_trial_balance.xml',
        'report/report_financial.xml',
        'report/report_tax.xml',
        'report/report_aged_partner.xml',
        'report/report_journal_audit.xml',
        'report/report_journal_entries.xml',

        'wizard/partner_ledger.xml',
        'wizard/general_ledger.xml',
        'wizard/trial_balance.xml',
        'wizard/balance_sheet.xml',
        'wizard/profit_and_loss.xml',
        'wizard/tax_report.xml',
        'wizard/aged_partner.xml',
        'wizard/journal_audit.xml',
        'wizard/cash_flow_report.xml',

        'views/financial_report.xml',
        'views/res_config_settings.xml',
        'views/menu_views.xml',
    ],
    'pre_init_hook': '_pre_init_clean_m2m_models',
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
