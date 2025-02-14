{
    "name": "Documents Management",
    "description": """
        Manager your documents:
            + Knowledge
            + Add and upload document
            + Manage extras store
                - SMB
                - SFTP
                - FTP

    """,
    "category": "Documents",
    "version": "1.0.1",
    "website": "https://www.odoobase.com/",
    "author": "DuyBQ",
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    "depends": [
        "base",
        "mail",
        'odb_base',
        'portal',
    ],
    'external_dependencies': {
        'python': ['pysmb'],
    },
    "data": [
        # "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/res_rules.xml",
        "security/res_users.xml",
        "security/ir.model.access.csv",

        "wizard/document_page_create_menu.xml",
        "wizard/document_page_show_diff.xml",

        "reports/report_document_page.xml",

        "views/document_page.xml",
        "views/document_page_category.xml",
        "views/document_page_history.xml",
        "views/document_connection.xml",
        "views/ir_attachment_view.xml",
        "views/res_config.xml",
        "views/menu_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'odb_document_management/static/src/scss/document_page.scss',
        ],
    },
    "demo": [
        "demo/document.xml",
        "demo/document_page.xml",
    ],
}
