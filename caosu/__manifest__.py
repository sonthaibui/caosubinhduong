{
    'name': 'Nhập Sản Lượng Cao Su',
    'version': '1.0.0',
    'sequence': -100,
    'category': 'Cao Su',
    'author': 'Cao Su Bình Dương',
    'website': 'https://www.caosubinhduong.com',
    'summary': 'Nhập sản lượng cao su công nhân cạo hằng ngày',
    'description': """Nhập sản lượng cao su công nhân cạo hằng ngày""",
    'depends': [
        'hr', 'mail', 'base', 'web',
        'report_xlsx', 'odb_sale_management'
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/sanluong.xml',
        'views/bangluong.xml',
        'views/luongvp.xml',
        'views/sanluongtn.xml',
        'views/nhapsanluong.xml',
        'views/nhapsanluongtn.xml',
        'views/phancay.xml',
        'views/hangcay.xml',
        'views/phancaytn.xml',
        'views/phucap.xml',
        'views/phucloi.xml',
        'views/xetthuong.xml',
        'views/xetai.xml',
        'views/phieuluong.xml',
        
        #'data/update_color.xml',  # Include the update script
        
        'report/reward_bymonth_report.xml',
        'report/rubber_salary_report.xml',
        'report/salary_office_report.xml',
        'report/salary_officer_report.xml',        
        'report/salaryboard_report.xml',
        'report/rubber_report.xml',
        'report/rubbertest_report.xml',  # Add this if not already present               
        'views/report_rubber_template.xml',
        'views/report_rubbertest_template.xml',       
        'views/menu_rubbertest_report.xml',
        'views/menu_rubber_report.xml',
        'views/rubber_config_views.xml',
        'views/rubber_price_wizard_views.xml',  # Load wizard views FIRST
        'views/rubber_price_views.xml',         # Then load price views that reference it
        'data/server_actions.xml',
        'views/tylehaohut_mu_views.xml',
    ],
    'controllers': [        
        'caosu/controllers/report_controller.py',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    
}