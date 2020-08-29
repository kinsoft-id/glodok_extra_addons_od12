# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Batch Picking Mass Action',
    'version': '11.0.1.1.0',
    'author': 'Kinsoft Indonesia, '
              'Kikin Kusumah',
    'website': 'https://kinsoft.id',
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': [
        'stock_account',
        'stock_picking_batch',
        'base_glodok',
    ],
    'data': [
        'wizard/mass_action_view.xml',
    ],
}
