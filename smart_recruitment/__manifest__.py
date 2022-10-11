# -*- coding: utf-8 -*-
{
    'name': "Gestion des recrutements",

    'summary': """
        Une application permet de gérer les recrutements du BinitNS avec un algorithme de recrutement intelligent.""",

    'description': """
        - Elimination des candidatures en double, Pré-sélection & Classification des candidats
        - Création des Workflows pour automatiser l'envoi des mails de recrutement et des candidatures 
    """,

    'author': "BinitNS - Binit Nearshore Services",
    'website': "http://www.binitns.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly8
    'depends': ['hr', 'mail', 'hr_recruitment', 'website_hr_recruitment'],

    # always loaded
    'data': [
        'views/smart_recruitement.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
    'auto_install': False,
    'installable': True,
}