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
        'security/groups.xml',
        'security/ir.model.access.csv', 
          

        'views/giaomu/domu_views.xml',
        'views/giaomu/rubber_price_views.xml',         # Then load price views that reference it
        'views/giaomu/rubber_price_wizard_views.xml',  # Load wizard views FIRST
        'views/giaomu/tylehaohut_mu_views.xml',
        'views/giaomu/xetai.xml',

        'views/inherit/hr_department_views.xml',
        
        'views/salary/bangluong.xml',
        'views/salary/luongvp.xml',
        'views/salary/phieuluong.xml',
        'views/salary/phucap.xml',
        'views/salary/phucloi.xml',
        'views/salary/xetthuong.xml',
        
        'views/sanluong/hangcay.xml',
        'views/sanluong/nhapsanluong.xml',
        'views/sanluong/phancay.xml',
        'views/sanluong/sanluong.xml',
        
        'views/thinghiem/nhapsanluongtn.xml',
        'views/thinghiem/phancaytn.xml',
        'views/thinghiem/sanluongtn.xml',
        
        'views/xembaocao/menu_rubber_report.xml',
        'views/xembaocao/menu_rubbertest_report.xml',
        'views/xembaocao/report_rubber_template.xml',
        'views/xembaocao/report_rubbertest_template.xml',
        'views/xembaocao/rubber_config_views.xml',        

        'views/xetthuong/yield_target_department_views.xml',
        'views/xetthuong/xetthuongnv.xml',
        
        'views/menu.xml',
        #'data/update_color.xml',  # Include the update script
        
        'report/reward_bymonth_report.xml',
        'report/rubber_salary_report.xml',
        'report/salary_office_report.xml',
        'report/salary_officer_report.xml',        
        'report/salaryboard_report.xml',
        'report/rubber_report.xml',
        'report/rubbertest_report.xml',  # Add this if not already present        
        
        'data/server_actions.xml',     
          
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