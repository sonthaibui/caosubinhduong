# -*- coding: utf-8 -*-

{
    'name':'Template Reports All in One',
    'category': 'Reports',
    'author': 'ThinhNguyen',
    'version': '1.0.9',
    'website': 'https://www.odoobase.com/',
    'description': """ Template Reports All in One""",
    'depends': ['web'],
    'summary':
        ' To Generate Reports for All module',
    'data': [
        'views/res_company_view.xml',
        'views/reports_format.xml',
        'views/res_config_setting.xml',
        'views/report_style_views.xml',
        'views/res_partner.xml',
        'security/ir.model.access.csv',

    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
