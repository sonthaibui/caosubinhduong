{
    'name': "Bank Payment VN",
    'summary': """
Payment Icons for banks in Vietnam""",
    'description': """
What it does
============
Technical module to provide Payment Icons for banks in Vietnam for other payment_* module to reuse
    """,
    'author': "DuyBQ",
    'website': "https://www.odoobase.com/",
    'category': 'Payment',
    'version': '1.0.1',
    'depends': ['odb_bank_payment'],
    'data': [
        'data/payment_icon_data.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
