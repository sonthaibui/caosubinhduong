{
    'name': 'Calculate Accounting Balance Of Statement',
    'version': '1.0.0',
    'sequence': -10,
    'category': 'Accounting',
    'author': 'Nicky Trinh',
    'website': 'https://www.facebook.com/trinhtannguyen19',
    'summary': 'Uodating Accounting Balance Of Statement After Changing One Statement',
    'description': """Uodating Accounting Balance Of Statement After Changing One Statement""",
    'depends': ['base','project','account','product','note','document_management_system','stock_account','odb_order_stock_cancel'],
    'data': [
        'views/extentviews.xml',
        'views/trangthai_views.xml',
        'views/project_task_views.xml',
        'security/ir.model.access.csv',
    ],        
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}