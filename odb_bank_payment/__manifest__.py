{
    'name': "Bank Payment",
    'summary': """
Payment""",
    'description': """
What it does
============
Technical module to provide Payment
    """,
    'author': "DuyBQ",
    'website': "https://www.odoobase.com/",
    'category': 'Payment',
    'version': '1.0.1',
    'depends': [
        'base',
        'account_payment',
    ],
    'data': [
        'views/res_bank_views.xml',
        'views/res_partner_bank_views.xml',
        'views/res_company_views.xml',
        'views/menu_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
