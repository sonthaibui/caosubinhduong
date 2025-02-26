{
    'name': 'Nhập Sản Lượng Cao Su',
    'version': '1.0.0',
    'sequence': -100,
    'category': 'Cao Su',
    'author': 'Cao Su Bình Dương',
    'website': 'https://www.caosubinhduong.com',
    'summary': 'Nhập sản lượng cao su công nhân cạo hằng ngày',
    'description': """Nhập sản lượng cao su công nhân cạo hằng ngày""",
    'depends': ['hr', 'mail'],
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
        'report/caosu_report.xml',],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}