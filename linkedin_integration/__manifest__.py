# -*- coding: utf-8 -*-
{
    'name': "Intégration LinkedIn",

    'summary': """
        Une application qui permet d'assurer des tâches de recrutement en utilisant LinkedIn dans Odoo.""",

    'description': """
        • Intégration & Synchronisation des offres d'emploi dans des outils tiers (LinkedIn) 
        • Collecte des profils LinkedIn (LinkedIn Web Scraper ou LinkedIn API) qui sont adaptés aux postes. 
    """,

    'author': "BinitNS - Binit Nearshore Services",
    'website': "http://www.binitns.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['auth_oauth', 'hr', 'hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/linkedin_integration.xml',
        'views/hr_linkedin.xml',
        'views/oauth_view.xml',
        'views/recruitment_config_settings.xml',
        'data/auth_linkedin_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
    'auto_install': False,
    'installable': True,
}
