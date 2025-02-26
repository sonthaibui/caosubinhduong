{
    'name': 'Farm Management',
    'summary': 'Help easily control Farm with ERP',
    'description': 'Farm Management',
    'category': 'Farm',
    'website': 'https://www.odoobase.com/',
    'author': 'DuyBQ, Nguyen NT',
    'version': '1.0.2',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'stock',
        'sale',
        'purchase',
        'hr',
        'maintenance',
    ],
    'data': [
        'security/res_group.xml',
        # 'security/ir_rules.xml',
        'security/ir.model.access.csv',

        'data/report_paperformat.xml',
        'data/ir_actions_server.xml',
        'data/ir_sequence.xml',
        'data/ir_actions_report.xml',

        'wizard/wizard_disable_farm_zone_views.xml',

        'report/farm_zone_report.xml',

        'views/farm_land_views.xml',
        'views/farm_zone_views.xml',
        'views/farm_job_views.xml',
        'views/farm_job_line_views.xml',
        'views/farm_job_operation_views.xml',
        'views/farm_stage_views.xml',
        'views/farm_produce_quality.xml',
        'views/farmer_team_views.xml',
        'views/hr_employee_views.xml',
        'views/ir_actions_report.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'assets': {
        'web.report_assets_common': [
            'odb_farm_management/static/src/css/style.css',
        ],
    },
}
