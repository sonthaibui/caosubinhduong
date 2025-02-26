# -*- coding: utf-8 -*-
{
    'name': 'Accounting Dynamic Reports',
    'version': '1.0.1',
    'category': 'Accounting',
    'summary': 'All in One Dynamic Accounting Reports For Odoo & Export the Report in PDF or Excel',
    'sequence': '10',
    'website': '',
    'depends': [
        'odb_account_reports_pdf'
    ],
    'demo': [],
    'data': [
        'report/report_account_pdf.xml',
        'report/dynamic_reports.xml',

        'views/dynamic_reports.xml',
        'views/menu_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'odb_account_dynamic_report/static/src/js/dynamic_reports_print.js',
            'odb_account_dynamic_report/static/src/js/dynamic_reports.js',
            'odb_account_dynamic_report/static/src/css/report_controller.css',
            'odb_account_dynamic_report/static/src/js/jquery-resizable.js',
        ],
        'web.assets_qweb': [
            'odb_account_dynamic_report/static/src/xml/report_control.xml',
        ],
        'odb_account_dynamic_report.assets': [
            'odb_account_dynamic_report/static/src/css/report_controller.css',
        ]
    },
}
