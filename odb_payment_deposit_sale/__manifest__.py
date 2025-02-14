{
    'name': "Payment Deposit for Sales",
    'summary': """
Payment Deposit for Sales""",
    'description': """
What it does
============
Technical module to provide Payment Deposit for Sales
    """,
    'author': "DuyBQ",
    'website': "https://www.odoobase.com/",
    'category': 'Payment',
    'version': '1.0.1',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'depends': [
        'sale_management',
        'odb_payment_deposit',
    ],
    'data': [
        'security/res_groups.xml',

        'wizards/wizard_payment_deposit_view.xml',

        'views/payment_deposit.xml',
        'views/account_payment_view.xml',
        'views/sale_order_view.xml',
        'views/menu_views.xml',

        'data/deposit_email_template.xml',
    ],
}
