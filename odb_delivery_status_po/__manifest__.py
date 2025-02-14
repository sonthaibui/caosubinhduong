# -*- coding: utf-8 -*-
{
    'name': "Delivery Status on Purchase Order",
    'summary': """Delivery Status on Purchase Order""",
    'description': "This module adds delivery status on purchase order",
    'author': "DuyBQ",
    'website': "https://www.odoobase.com",
    'category': 'Purchase',
    'version': '1.0.1',
    'depends': [
        'purchase',
        'stock',
        'purchase_stock'
    ],
    'data': [
        'views/purchase_order.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'qweb': [],
}
