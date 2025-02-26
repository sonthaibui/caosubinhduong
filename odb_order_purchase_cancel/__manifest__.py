# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Cancel Order',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Order Cancel',
    'summary': """ All Cancel all related Purchase order
    """,

    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'purchase_stock',
        'odb_order_invoice_cancel',
        'odb_order_stock_cancel'
    ],
    'data': [
        'views/view_purchase_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
