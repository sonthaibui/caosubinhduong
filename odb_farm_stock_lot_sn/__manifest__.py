# -*- coding: utf-8 -*-
{
    'name' : 'Lot with Quality on Farm',
    'version' : '1.0.1',
    'author':'DuyBQ',
    'category': 'Farm',
    'summary': """ Lot with Quality""",
    'website': 'https://www.odoobase.com/',
    'license': 'OPL-1',
    'depends' : [
        'odb_farm_management',
        'odb_stock_lot_quality',
        'odb_stock_lot_quality_sale',
    ],
    'data': [
        'security/ir.model.access.csv',


    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
