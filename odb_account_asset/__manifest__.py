# -*- coding: utf-8 -*-
{
    'name': 'Account Assets Management',
    'description': """Manage assets owned by a company or a person. 
        Keeps track of depreciation's, and creates corresponding journal entries""",
    'summary': 'Finance Assets Management',
    'version': '1.0.1',
    'author': 'DuyBQ',
    'depends': [
        'account',
    ],
    'category': 'Accounting',
    'sequence': 10,
    'website': 'https://www.odoobase.com/',
    'data': [
        'data/account_asset_data.xml',

        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',

        'report/account_asset_report_views.xml',

        'views/account_asset_category_views.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
        'views/product_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odb_account_asset/static/src/scss/account_asset.scss',
            'odb_account_asset/static/src/js/account_asset.js',
        ],
        'web.qunit_suite_tests': [
            ('after', 'web/static/tests/legacy/views/kanban_tests.js', '/odb_account_asset/static/tests/account_asset_tests.js'),
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
