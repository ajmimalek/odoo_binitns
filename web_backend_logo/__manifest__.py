{
    'name': "BackOffice - Logo BinitNS",
    'description': """
        - Ajout du Logo BinitNS à la barre de navigation principale.
    """,
    'author': "Kareem Abuzaid, Edited By BinitNS Company",
    'version': "13.0.1.0",
    'website': "http://www.binitns.com/",
    'license': "AGPL-3",
    'depends': [
        'base',
        'web',
    ],
    'qweb': [
        "static/src/xml/menu.xml",
    ],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
}
