# __manifest__.py
{
    'name': 'Delivery Order Direct Print',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Print delivery orders directly to a dot matrix printer',
    'description': 'This module allows direct printing of delivery orders to a dot matrix printer. sudo apt-get install lpr',
    'author': 'Kikin Kusumah',
    'depends': ['stock'],
    'data': [
        'reports/delivery_order_report.xml',
    ],
    'installable': True,
    'application': False,
}
