# -*- coding: utf-8 -*-
{
    "name": "Report Stock",
    "author": "ThinhNguyen",
    "website": "https://www.odoobase.com/",
    "category": "Reports",
    "summary": "Report for Stock",
    "description": """Report for Stock""",
    "version": "1.0.1",
    "depends": [
        "stock",
        "stock_picking_batch",
        "odb_reports_base",
    ],
    "application": True,
    "data": [
        'data/report_paperformat.xml',
        'data/ir_actions_report_qweb.xml',
        'report/stock_picking/stock_template3.xml',
        'report/stock_picking/stock_template4.xml',
        'report/stock_picking/stock_template1.xml',
        'report/stock_picking/stock_template2.xml',
        'report/stock_picking/stock_template_delivery_orders.xml',
        'report/stock_picking/stock_template_receipts.xml',

        'report/stock_delivery/stock_delivery_template3.xml',
        'report/stock_delivery/stock_delivery_template4.xml',
        'report/stock_delivery/stock_delivery_template1.xml',
        'report/stock_delivery/stock_delivery_template2.xml',
        'report/stock_delivery/stock_delivery_template5.xml',

        # 'report/inventory_adj/adj_template1.xml',
        # 'report/inventory_adj/adj_template2.xml',
        # 'report/inventory_adj/adj_template3.xml',
        # 'report/inventory_adj/adj_template4.xml',
        # 'report/inventory_adj/default_template.xml',

        'report/stock_picking_batch/stock_picking_batch_template1.xml',
        'report/swich_template/switch_template.xml',
        'views/report_template_setting.xml',

    ],
    "auto_install": False,
    "installable": True,
}
