# -*- coding: utf-8 -*-
# Copyright 2016, 2017 La Jayuhni Yarsyah
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Glodok Base",
    "summary": "Glodokelektronik.net base module",
    "version": "11.0.1.0.1",
    "category": "base",
    
	"description": """
		Glodokelektronik.net base module
    """,
	'images':[
        
	],
    "author": "La Jayuhni Yarsyah",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'base','mail','stock','stock_picking_batch','account_invoicing','sale_management','purchase',
        'region','sale_stock'
    ],
    "data": [
        

        'views/paper_format.xml',
        'views/external_layout.xml',

        'views/stock_picking/report_delivery_slip.xml',
        

        'views/invoices/view.xml',
        'views/invoices/external_layout.xml',
        'views/invoices/report_invoice_a6.xml',

        # 'views/purchase/purchase.xml',

        'views/stock_picking/action.xml',
        'views/stock_picking/view.xml',
        'views/stock_picking_batch/view.xml',
        
        'views/stock_picking_create_batch_wizard/view.xml',


        'views/sales/view.xml',
        'views/stock_move/view.xml',
        'views/stock_warehouse/view.xml',
        'views/stock_move_line/view.xml',

        'views/contacts/view.xml',


        'views/stock_picking_type/views.xml',
        'views/stock_picking_type/actions.xml',
        'views/res_users/view.xml',

        'security/delivery_groups.xml',
        'security/stock_picking_batch_report.xml',

        'views/wizard/pickup_validation.xml',
        'views/wizard/picking_batch_has_return.xml',

        'security/invoice.xml',

        'views/stock_picking_batch/report_memo.xml',



        # 'data/location.xml',
    ],
}

