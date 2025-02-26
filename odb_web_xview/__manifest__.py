# -*- coding: utf-8 -*-
{
    'name': "XView Extraview",
    'description': """
        Add Xview, a view which can show level relationship via tree on FormView
    """,
    "version": "1.0.2", 
    "category": "Web",
    'author': "DuyBQ",
    'depends': [
        'web'
    ],
    "website": "https://www.odoobase.com/",
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            '/odb_web_xview/static/src/js/xview_view.js',
            '/odb_web_xview/static/src/js/xview_model.js',
            '/odb_web_xview/static/src/js/xview_renderer.js',
            '/odb_web_xview/static/src/js/xview_controller.js',

            '/odb_web_xview/static/src/css/awesomeStyle/fa.scss',
            '/odb_web_xview/static/src/css/awesomeStyle/awesome.scss',
            '/odb_web_xview/static/src/scss/variables.scss',
            '/odb_web_xview/static/src/scss/views.scss',

            '/odb_web_xview/static/src/libs/jquery.xview.core.js',
            '/odb_web_xview/static/src/js/widget_xview.js',

        ],
        'web.assets_qweb': [
            'odb_web_xview/static/src/xml/web_xview.xml',
        ],
    },
    'installable': True,
    'auto_install': False
}
