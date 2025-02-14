# -*- coding: utf-8 -*-
{
    'name': 'Web List Sequence',
    'version': '1.0.1',
    'category': 'Tools',
    'description': """
Show the sequence number for each line in list view / x2many list view.
    """,
    'website': 'https://www.odoobase.com',
    'author': 'DuyBQ',
    'license': 'OPL-1',
    'depends': [
        'web',
    ],
    'data': [],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'odb_web_list_sequence/static/src/js/list_renderer.js',
            'odb_web_list_sequence/static/src/scss/base.scss',


        ],
    },
}
