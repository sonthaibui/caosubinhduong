{
    'name': 'Accounting Analytic Report',
    'description': 'Accounting Analytic Reports',
    'summary': 'Accounting Analytic Reports',
    'version': '1.0.1',
    'author': 'NguyenTV',
    'website': 'https://www.odoobase.com/',
    'category': 'Accounting',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/report_financial.xml',
        'views/search_template_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'odb_account_analytic_report.assets_financial_report': [
            ('include', 'web._assets_helpers'),
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),
            'web/static/fonts/fonts.scss',
            'odb_account_analytic_report/static/src/scss/account_financial_report.scss',
            'odb_account_analytic_report/static/src/scss/account_report_print.scss',
        ],
        'web.assets_backend': [
            'odb_account_analytic_report/static/src/js/mail_activity.js',
            'odb_account_analytic_report/static/src/js/account_reports.js',
            'odb_account_analytic_report/static/src/js/action_manager_account_report_dl.js',
            'odb_account_analytic_report/static/src/scss/account_financial_report.scss',
        ],
        'web.qunit_suite_tests': [
            'odb_account_analytic_report/static/tests/action_manager_account_report_dl_tests.js',
            'odb_account_analytic_report/static/tests/account_reports_tests.js',
        ],
        'web.assets_tests': [
            'odb_account_analytic_report/static/tests/tours/**/*',
        ],
        'web.assets_qweb': [
            'odb_account_analytic_report/static/src/xml/**/*',
        ],
    }
}
