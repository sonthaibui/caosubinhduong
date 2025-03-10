{
    'name': 'General',
    'version': '1.0.0',
    'sequence': -10,
    'category': 'Custom',
    'author': 'Son Bui',
    'website': 'https://www.facebook.com/trinhtannguyen19',
    'summary': 'Modify core app',
    'description': "",
    'depends': ['base','project','account','product','note','document_management_system','stock_account','odb_order_stock_cancel'],
    'data': [               
                
        'views/product_template_views.xml',        
        'views/project_views.xml',
        'views/project_task_views.xml',
        #'views/project_task_kanban_views.xml',
        'views/ir_module_module_views.xml',
        'data/ir_module_module_actions.xml',
        'data/ir_project_task_action.xml',
        
            ],        
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}