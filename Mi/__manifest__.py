{
    'name': 'Cassava Management',
    'version': '1.0',
    'summary': 'Module for managing Lomi fields',
    'description': 'A module to manage the planting and caring for Lomi',
    'author': 'Bùi Thái Sơn',
    'depends': ['base', 'product', 'calculate_accounting_balance'],
    'data': [
        'security/ir.model.access.csv',
        'views/lomi_views.xml',
        'views/bonphan_line_views.xml',
    ],
    'installable': True,
    'application': True,
}