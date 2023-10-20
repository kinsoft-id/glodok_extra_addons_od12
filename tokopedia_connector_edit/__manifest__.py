{
    'name': "Tokopedia Connector",
    'version': '1.0',
    'depends': ['base','sale', 'web'],
    'author': "Yugi",
    'category': 'Category',
    'description': """
    Description text
    """,
    'data': [
        'data/ir_cron.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/tokopedia_shop.xml',
        'views/tokopedia_connector.xml',
        'views/sale_order.xml',
        'views/tokopedia_shop_detail.xml',
        # 'views/account_invoice.xml',
        'views/stock_picking.xml',
        'wizard/tp_conn_wizard.xml',
        'wizard/download_label.xml',
    ],
}