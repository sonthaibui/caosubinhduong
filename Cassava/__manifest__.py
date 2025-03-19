{
    'name': 'Quản lý Lô Mì',
    'version': '1.0',
    'sequence': -102,
    'category': 'Cassava',
    'summary': 'Management of Cassava',
    'description': """
        This module manages Lô mì with related information such as bón phân, giống mì, kiểu trồng, etc.
    """,
    'depends': ['base', 'product', 'calculate_accounting_balance'],
    'data': [
        'data/dummy_currency.xml',  # Include the dummy currency data file
        'views/bonphan_views.xml',
        'views/bonphan_line_views.xml',
        'views/lomi_views.xml',                
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}