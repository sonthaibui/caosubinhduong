# -*- coding: utf-8 -*-
{
    'name': "Stock Transfers Backdate",
    'author': 'DuyBQ',
    'website': 'https://www.odoobase.com/',
    'category': 'Warehouse',
    'version': '1.0.1',
    'summary': """
Manual validation date for stock transfers.
        """,

    'description': """
In Odoo, when you validate a stock transfer, Odoo applies the current time for the transfer date automatically which is sometimes not what you want.
For example, you input data for the past.
    """,
    'depends': ['stock_account', 'odb_stock_management'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_group.xml', 
        'wizard/stock_picking_backdate_views.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'application': False,
    'installable': True,
}
