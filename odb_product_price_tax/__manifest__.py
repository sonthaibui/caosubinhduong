# -*- coding: utf-8 -*-
{
    'name': "Sale Price with Tax",
    'version': '1.0.1',
    'summary': 'Add sale price with tax on Product Template',
    'description': """
Add sale price with tax on Product Template.
=================
    """,
    'author': "DuyBQ",
    'website': "https://www.odoobase.com/",
    'category': 'Products',
    'depends': [
        'product',
    ],
    'data': [
        # 'security/ir.model.access.csv',

        'data/ir_actions_server.xml',

        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
