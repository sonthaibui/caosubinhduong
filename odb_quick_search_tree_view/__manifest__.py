# -*- coding: utf-8 -*-
{
    'name': "Tool Quick Search Tree View",
    'summary': """
        This app will allow app to manage the List Views on the fly and endeavour a quick and effortless way to 
        view/manage the desired data, where you’ve multifarious options to slice and dice your List View easily
        on a click.
         """,
    'description': """
        List View ,
        Advance Search ,
        Read/Edit Mode ,
        Dynamic List ,
        Hide/Show list view columns ,
        List View Manager ,
    """,
    'sequence': 15,
    'category': 'Tools',
    'version': '1.0.1',
    'author': "DuyBQ",
    'website': "https://www.odoobase.com/",
    'license': 'OEEL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': [
        'base',
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',

        'views/res_config_settings.xml',
        'views/menu_views.xml',
    ],
    'assets': { 

        'web.assets_backend': [ 
            '/odb_quick_search_tree_view/static/lib/spectrum/spectrum.css',
            '/odb_quick_search_tree_view/static/lib/spectrum/spectrum.js',
            '/odb_quick_search_tree_view/static/lib/stickytableheaders/jquery.stickytableheaders.js',
            '/odb_quick_search_tree_view/static/lib/resizableColumns/jQuery.ResizableColumns.js',

            '/odb_quick_search_tree_view/static/src/css/list_view_manager.scss',
            '/odb_quick_search_tree_view/static/src/js/list_view_manager_view.js',
            '/odb_quick_search_tree_view/static/src/js/list_view_manager_controller.js',
            '/odb_quick_search_tree_view/static/src/js/list_view_manager_renderer.js',
            '/odb_quick_search_tree_view/static/src/js/color_picker.js',
         ],
        'web.assets_qweb': [
            'odb_quick_search_tree_view/static/src/xml/**/*',
        ],
     },
    'post_init_hook': 'post_install_hook',
    'uninstall_hook': 'uninstall_hook',
}
