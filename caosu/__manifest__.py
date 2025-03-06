{
    'name': 'Nhập Sản Lượng Cao Su',
    'version': '1.0.0',
    'sequence': -100,
    'category': 'Cao Su',
    'author': 'Cao Su Bình Dương',
    'website': 'https://www.caosubinhduong.com',
    'summary': 'Nhập sản lượng cao su công nhân cạo hằng ngày',
    'description': """Nhập sản lượng cao su công nhân cạo hằng ngày""",
    'depends': ['hr', 'mail', 'base', 'web'],
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
        #'views/assets.xml',
        'report/reward_bymonth_report.xml',
        'report/rubber_salary_report.xml',
        'report/salary_office_report.xml',
        'report/salary_officer_report.xml',        
        'report/salaryboard_report.xml',
        ],
    '''assets': {
        'web.assets_backend': [
            #'caosu/static/src/js/pivot_widget.js',
            #'caosu/static/src/css/color.css',
        ],
    },'''
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}