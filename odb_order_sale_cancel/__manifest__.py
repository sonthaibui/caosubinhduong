# -*- coding: utf-8 -*-
{
    'name' : 'Sales Cancel Order',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ All Cancel all related Sales order""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'sale_management',
        'sale_stock',
        'odb_order_invoice_cancel',
        'odb_order_stock_cancel'
    ],
    'data': [
        'views/view_sale_order.xml',

    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
