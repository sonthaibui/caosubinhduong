{
    'name': "Purchase Managerment",
    'summary': """Purchase Managerment""",
    'description': """Purchase Managerment""",
    'category': 'Purchase',
    'version': '1.0.1',
    'website': 'https://www.odoobase.com/',
    'author': "ThinhNguyen",
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'qweb': [],
    'depends': [
        'purchase',
        'odb_base',
        'report_xlsx',
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'reports/ir_actions_report.xml',
        'wizard/wizard_import_purchase_order.xml',
        'wizard/wizard_import_purchase_order_line.xml',

        'views/purchase_order.xml',
        'views/purchase_quotation.xml',
        'views/res_partner.xml',
        'mail/purchase_order_confirm_mail.xml',
        'views/purchase_order_line.xml',
        'views/menu_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'odb_purchase_management/static/src/css/custom.css',
        ],
        'web.assets_qweb': [
            ],
        'odb_purchase_management.assets': [

        ]
    },
}
