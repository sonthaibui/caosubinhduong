# -*- coding: utf-8 -*-
{
    'name': "Delivery Status on Sale Order",
    'summary': """Delivery Status on Sale Order""",
    'description': "This module adds Delivery Status on Purchase Order",
    'author': "DuyBQ",
    'website': "https://www.odoobase.com",
    'category': 'Sales',
    'version': '1.0.1',
    'depends': [
        'sale_stock',
        'sale_management'
    ],
    'data': [
        'views/sales_order.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
