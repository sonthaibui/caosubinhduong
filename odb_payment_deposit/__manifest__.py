{
    'name': "Payment Deposit",
    'summary': """
Payment Deposit""",
    'description': """
What it does
============
Technical module to provide Payment Deposit
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
        'base',
        'payment'
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'wizards/wizard_payment_deposit_view.xml',

        'views/payment_deposit.xml',
    ],
}
