{
    'name': 'Glodok Security Rules',
    'summary': """
        Glodok Security Rules
        """,
    'version': '0.0.1',
    'category': 'glodok,security',
    "author": "La Jayuhni Yarsyah",
    'description': """
        Security rules modules, modul tambahan karena perubahan user access dan roles
    """,
    'depends': [
        'base_glodok',
    ],
    'data': [
    	'security/ir.model.access.xml',
    	'views/menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True    
}