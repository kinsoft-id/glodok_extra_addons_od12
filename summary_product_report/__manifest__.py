{
    'name': 'Summary Product Report',
    'summary': """
        Summary Product Report
        """,
    'version': '0.0.1',
    'category': 'product,reporting',
    "author": "La Jayuhni Yarsyah",
    'description': """
        Summary Product Report
    """,
    'depends': [
        'stock','product','sale','purchase'
    ],
    'data': [
        'data/config_parameter.xml',
    	'security/ir.model.access.csv',
    	'reports/last_movement_product_report/views.xml',

        'reports/product_sales_qty_report/view.xml',
        'reports/product_sale_daily_average/view.xml',
        # 'reports/last_movement_product_report_7_14/views.xml',
        # 'reports/last_movement_product_report_15_30/views.xml',
        # 'reports/last_movement_product_report_30/views.xml',

        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True    
}