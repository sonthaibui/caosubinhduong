# -*- coding: utf-8 -*-
{
    'name': "Sale Management",

    'summary': """
        + Quotation Revision History
        + Reminder Quotation
        + Split Order
        + Add commitment date to sale line
        + Custom product sale line
        + Custom product component sale line
    """,

    'description': """
        Sale Management
    """,
    'author': "Thinh.NV, Duy.BQ",
    'website': "https://www.odoobase.com/",
    'category': 'Sales',
    'version': '1.0.1',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': [
        'base',
        # 'sale_margin',
        'sale_management',
        # 'sale_mrp',
        'sale_stock',
        'odb_base',
        # 'report_py3o',
        # 'erpvn_contact_management',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        
        'data/sale_due_remainder_email.xml',
		'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',
        'data/report_paperformat.xml',

        'reports/ir_actions_report.xml',
        'wizard/wizard_import_sale_order.xml',
        'wizard/wizard_import_sale_order_line.xml',

        'mail/order_confirmation_successful_mail_template.xml',

        'wizard/wizard_split_sale_order.xml',

        'reports/views/sale_report_views.xml',
        'reports/views/report_sale_order.xml',
        'reports/views/report_delivery_date_order.xml',
        'reports/views/report_detaill_order.xml',

        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/component_attribute.xml',
        'views/stock_picking.xml',
        'views/quotation_history.xml',
        'views/quotation_history_line.xml',
        'views/product_template_view.xml',
        'views/account_incoterm.xml',
        'views/res_partner.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'odb_sale_management.assets': [
            'odb_sale_management/static/src/scss/resize_column.scss',
            'odb_sale_management/static/src/scss/fonts.scss',
        ]
    },
}
