# -*- coding: utf-8 -*-
{
    'name': "Customize Odoo 11 for Setia Mandiri Elektronik",

    'summary': """
        Customize Odoo 11
        """,

    'description': """
        - Give a warning if product price set lower than the product cost
    """,

    'author': "Kinsoft Indonesia, Kikin Kusumah",
    'website': "https://kinsoft.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Utilities',
    'version': '11.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sale_order_views.xml',
    ],
    'application': True,
}
