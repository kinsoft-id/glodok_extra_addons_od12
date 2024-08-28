# -*- coding: utf-8 -*-
{
    'name': 'Hide Product Stock',
    'summary': """Product Stock Will be Visible Only for Specified Group""",
    'version': '11.0.1.1.0',
    'description': """Product stock will be visible only for specified group""",
    'author': 'Kikin Kusumah',
    'company': 'Kinsoft Indonesia',
    'website': 'https://www.kinsoft.id',
    'category': 'Stock',
    'depends': ['base', 'stock'],
    'license': 'AGPL-3',
    'data': [
        'security/view_product_stock.xml',
        'views/hide_product_stock.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
