# -*- coding: utf-8 -*-
{
    'name': "Gestion des recrutements",

    'summary': """
        Une application permet de gérer les recrutements du BinitNS avec un algorithme de recrutement intelligent. """,

    'description': """
        - Elimination des candidatures en double, Pré-sélection & Classification des candidats, Collecte des profils LinkedIn en recherche d'emploi
        - Création des Workflows pour automatiser l'envoi des mails de recrutement et des candidatures 
        - Intégration & Synchronisation des offres d'emploi dans des outils tiers (Linkedin, TanitJobs, etc.)
    """,

    'author': "BinitNS - Binit Nearshore Services",
    'website': "http://www.binitns.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'module_category_operations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'hr_recruitment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
