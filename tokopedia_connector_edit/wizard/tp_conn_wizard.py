from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

ORDER_STATUS_DICT = {
    0: 'Seller cancel order.',
    2: 'Order Reject Replaced.',
    3: 'Order Reject Due Empty Stock.',
    4: 'Order Reject Approval.',
    5: 'Order Canceled by Fraud',
    10: 'Order rejected by seller.',
    11: 'Order Pending Replacement.',
    15: 'Order canceled by system due buyer request.',
    100: 'Pending order.',
    103: 'Wait for payment confirmation from third party.',
    200: 'Payment confirmation.',
    220: 'Payment verified, order ready to process.',
    221: 'Waiting for partner approval.',
    400: 'Seller accept order.',
    450: 'Waiting for pickup.',
    500: 'Order shipment.',
    501: 'Status changed to waiting resi have no input.',
    520: 'Invalid shipment reference number (AWB).',
    530: 'Requested by user to correct invalid entry of shipment reference number.',
    540: 'Delivered to Pickup Point.',
    550: 'Return to Seller.',
    600: 'Order delivered.',
    601: 'Buyer open a case to finish an order.',
    690: 'Fraud Review',
    691: 'Suspected Fraud',
    695: 'Post Fraud Review',
    698: 'Finish Fraud Review',
    699: 'Order invalid or shipping more than 25 days and payment more than 5 days.',
    700: 'Order finished.',
    701: 'Order assumed as finished but the product not arrived yet to the buyer.',
}

ORDER_STATUS = [(i, ORDER_STATUS_DICT.get(i, 'Reserved by Tokopedia.')) for i in range(0, 1000) if i in [k for k in ORDER_STATUS_DICT.keys()]]

class TpConnWizard(models.TransientModel):
    _name = 'tp.conn.wizard'

    def default_tp_conn_id(self):
        return self.env['tokopedia.connector'].sudo().search([('is_connected','=',True)], limit=1).id
    
    tp_conn_id = fields.Many2one('tokopedia.connector', string='Connector', default=default_tp_conn_id, required=True)
    order_from_date = fields.Date(default=fields.Date.today(), required=True)
    order_to_date   = fields.Date(default=fields.Date.today(), required=True)
    # order_from_date = fields.Datetime(default=datetime.now(), required=True)
    # order_to_date   = fields.Datetime(default=datetime.now(), required=True)
    state_order     = fields.Selection(ORDER_STATUS, string='State Order', required=False, default=400)

    def action_sync(self):
        date_from = self.order_from_date + ' 00:00:00'
        date_to   = self.order_to_date +' 23:59:59'
        # date_from = self.order_from_date
        # date_to   = self.order_to_date
        # print(date_from)
        self.tp_conn_id.with_context({'date_from': date_from, 'date_to': date_to}).button_sync_shop()
        # action = self.env.ref('tokopedia_connector.tokopedia_shop_detail_action').read()[0]
        # action['name']   = 'Order from %s to %s' % (date_from, date_to)
        # action['domain'] = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]
        # return action
