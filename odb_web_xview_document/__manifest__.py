{
    'name': "Document with XView",

    'summary': """
        This module is used to link between document_managemnt and xview
        Use case: when remove xview , prevent to remove module depended xview
        """,

    'description': """
        This module is used to link between document_managemnt and xview
        Use case: when remove xview , prevent to remove module document_managemnt depended xview
    """,

    'author': "LuanTM",
    'website': "https://www.odoobase.com/",
    'category': 'Web',
    'version': '0.1',
    'depends': ['odb_document_management','odb_web_xview'],
    'data': [
        'views/document_page_view.xml',
    ],
    'uninstall_hook': "uninstall_hook",
}
