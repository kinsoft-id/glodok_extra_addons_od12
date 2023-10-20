from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import tzlocal
import pytz
import requests
import json
import time

import logging
_logger = logging.getLogger(__name__)
BASE_URL = 'https://fs.tokopedia.net'
ORDER_STATUS_DICT = {
    0: 'Seller cancel order.',
    2: 'Order Reject Replaced.',
    3: 'Order Reject Due Empty Stock.',
    4: 'Order Reject Approval.',
    5: 'Order Canceled by Fraud',
    6: 'Order Rejected (Auto Cancel Out of Stock)',
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

class TokopediaShop(models.Model):
    _name = 'tokopedia.shop'

    shop_id = fields.Integer(string='Shop ID')
    shop_name = fields.Char(string='Shop')
    shop_url = fields.Char(string='Shop Url')
    tp_conn_id = fields.Many2one('tokopedia.connector', string='Tp Conn')
    tp_user_id = fields.Integer(string='Tp User Id')
    province_name = fields.Char(string='Province Name')
    date_shop_created = fields.Date(string='Date Shop Created')
    user_id = fields.Integer(string='Tp User ID')
    tokopedia_shop_line_ids = fields.One2many('tokopedia.shop.detail', 'tokopedia_shop_id', 'Line')
    total_inv = fields.Integer(string='Total Invoice', compute='_compute_total_inv')

    def get_utc_datetime(self, dt, as_tz, dt_format=False):
        if not any([isinstance(dt, datetime), isinstance(dt, str)]):
            return False
        elif isinstance(dt, str):
            if not dt_format:
                return False
            dt = datetime.strptime(dt, dt_format)
        return pytz.timezone(as_tz).localize(dt).astimezone(pytz.UTC)
    
    def get_tp_dt_format(self, attr_name):
        dt_formats = {
            'create_time': '%Y-%m-%dT%H:%M:%S.%fZ',
            'payment_date': '%Y-%m-%dT%H:%M:%SZ'
        }
        return dt_formats.get(attr_name)
    
    def get_tracking(self, so, tp_invoice_number):
        # _logger.warn('action_view_tracking')
        try:
            self.ensure_one()
            single_order_url = '%s/v2/fs/%s/order?invoice_num=%s' % (
                BASE_URL,
                self.tp_conn_id.app_id,
                tp_invoice_number
            )
            Auth = '%s %s' % (self.tp_conn_id.token_type, self.tp_conn_id.access_token)
            req = requests.get(single_order_url, headers={
                'Authorization': Auth
            })
            headers = req.headers
            req.raise_for_status()
            response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}
            datas_single = response.get('data') if req.status_code == 200 else {}
            self._cr.execute("""delete from tokopedia_tracking where order_id = %s"""%(so))
            for t in datas_single["order_info"]["order_history"]:
                self.env['tokopedia.tracking'].sudo().create({
                    'order_id'  : so,
                    'action_by' : t.get('action_by'),
                    'message'   : t.get('message'),
                    'comment'   : t.get('comment'),
                    'date'      : pytz.timezone('Asia/Jakarta').localize(datetime.strptime(t.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(pytz.UTC),
                })
        except Exception as ex:
            _logger.error(ex)
            raise ValidationError(ex)

    @api.multi
    def get_order(self, date_from , date_to):
        format_date = "%Y-%m-%d %H:%M:%S"
        try:
            for rec in self:
                if date_from and date_to:
                    from_date = datetime.strptime(date_from, format_date) 
                    to_date = datetime.strptime(date_to, format_date)
                else:
                    from_date = datetime.strptime(rec.tp_conn_id.order_from_date, format_date) 
                    to_date = datetime.strptime(rec.tp_conn_id.order_to_date, format_date)

                
                server_timezone = tzlocal.get_localzone().zone
                dss_utc = pytz.timezone(server_timezone).localize(from_date).astimezone(pytz.UTC)
                des_utc = pytz.timezone(server_timezone).localize(to_date).astimezone(pytz.UTC)
                dss_tokopedia = dss_utc + timedelta(hours=7)
                des_tokopedia = des_utc + timedelta(hours=7)
                timestamp_start_tokopedia = int(dss_tokopedia.timestamp())
                timestamp_end_tokopedia = int(des_tokopedia.timestamp())

                # Get All order
                Auth = '%s %s' % (rec.tp_conn_id.token_type, rec.tp_conn_id.access_token)

                page = 1
                per_page = 9999
                # per_page = 1
                all_order_url = '%s/v2/order/list?fs_id=%s&shop_id=%s&from_date=%s&to_date=%s&page=%s&per_page=%s' % (
                    BASE_URL,
                    rec.tp_conn_id.app_id,
                    rec.shop_id,
                    timestamp_start_tokopedia,
                    timestamp_end_tokopedia,
                    page,
                    per_page
                )
                r = requests.get(all_order_url, headers={
                    'Authorization': Auth
                })
                r.raise_for_status()
                response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
                result = response.get('header', {"status_code": r.status_code})
                if result:
                    result["url"] = all_order_url
                    result['date'] = {
                        "date_to": des_tokopedia.strftime("%A, %d %B %Y %H:%M:%S"),
                        "date_start": dss_tokopedia.strftime("%A, %d %B %Y %H:%M:%S")
                    }
                    data_results = response.get('data') if response.get('data') else []
                    # print('===============ALL ORDER===============')
                    # print(json.dumps(data_results, indent=2))
                    result['data_results'] = len(data_results)
        except Exception as e:
            _logger.error(e)
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
        # End Get All order
        else:
            headers = r.headers
            if headers.get('X-Ratelimit-Remaining') and headers.get('X-Ratelimit-Remaining') == '1':
                time.sleep(1)
                
            datas = response.get('data') if r.status_code == 200 else []
            # print('datas', datas)
            new_order_datas = []
            if datas:
                new_order_datas = [new_order for new_order in datas]
                # new_order_datas = [new_order for new_order in datas if new_order.get('order_status') and new_order.get('order_status') not in [0, 2, 3, 4, 5, 10, 15, 550]]
                # new_order_datas = [new_order for new_order in datas if new_order.get('order_status') and new_order.get('order_status') in [100, 400, 450, 500, 501, 520, 530, 540, 600, 601, 690, 691, 695, 698, 699, 700, 701]]
                # new_order_datas = [new_order for new_order in datas if new_order.get('order_status') and new_order.get('order_status') in [rec.tp_conn_id.state_order]]
            if new_order_datas:
                for data in new_order_datas:
                    single_order_url = '%s/v2/fs/%s/order?invoice_num=%s' % (
                        BASE_URL,
                        rec.tp_conn_id.app_id,
                        data.get('invoice_ref_num')
                    )
                    req = requests.get(single_order_url, headers={
                        'Authorization': Auth
                    })
                    headers = req.headers
                    if headers.get('X-Ratelimit-Remaining') and headers.get('X-Ratelimit-Remaining') == '1':
                        time.sleep(1)
                    req.raise_for_status()
                    response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}

                    datas_single = response.get('data') if req.status_code == 200 else {}
                    # print('=============================Data Buyer=============================')
                    # print(json.dumps(data['buyer'], indent=2))
                    # print(json.dumps(datas_single['buyer_info'], indent=2))
                    # print('=============================Data Bundle=============================')
                    # print("Have Bundle" + json.dumps(data['have_product_bundle'], indent=2))
                    # print("Bundle" + json.dumps(data['bundle_detail'], indent=2))

                    # self._cr.execute(""" select id from sale_order where tp_invoice_number = %s """,[datas_single['invoice_number']])
                    # tokopedia_order_id = self._cr.fetchone()
                    # print(tokopedia_sale_order)
                    tokopedia_order = self.env['sale.order'].search([('tp_invoice_number', '=', datas_single['invoice_number'])], limit=1)
                    print(tokopedia_order)
                    if tokopedia_order:
                        # logistic_name = datas_single['order_info']['shipping_info']['logistic_name']
                        # # logistic_obj = self.env['tokopedia.logistic'].search([('name', '=', logistic_name)])
                        # self._cr.execute(""" select id from tokopedia_logistic where name = %s """,[logistic_name])
                        # logistic_id = self._cr.fetchone()
                        # tokopedia_order = self.env['sale.order'].browse(tokopedia_order_id)
                        # tokopedia_order.tp_order_status = datas_single['order_status']

                        tokopedia_order.write({
                            'tp_order_status': datas_single['order_status'],
                            # 'logistic_id' : logistic_id,
                        })
                        if not tokopedia_order.shipping_label_data:
                            tokopedia_order.shipping_label_download()
                            tokopedia_order.get_buyer_info()

                        if datas_single['order_status'] in [200, 220, 221, 400, 450, 500, 501, 520, 530, 540, 600, 601, 690, 691, 695, 698, 699, 700, 701] and tokopedia_order.state == 'draft':
                        # # if tokopedia_order.state == 'draft':
                            tokopedia_order.action_confirm()
                            tokopedia_order.action_invoice_create()
                            self._cr.commit()
                    else:                  

                        logistic_name = datas_single['order_info']['shipping_info']['logistic_name']
                        # logistic_obj = self.env['tokopedia.logistic'].search([('name', '=', logistic_name)])
                        self._cr.execute(""" select id from tokopedia_logistic where name = %s """,[logistic_name])
                        logistic_id = self._cr.fetchone()

                        buyer_full_name = datas_single['buyer_info']['buyer_fullname'] if datas_single['buyer_info']['buyer_fullname'] else "Tokopedia Buyer [ID %s]" % (data['buyer']['id'])
                        # customer_order_id = self.env['res.partner'].search([('ref', '=', "TP%s" % (data['buyer']['id']))])
                        # if not customer_order_id:
                        customer_order_id = self.env['res.partner'].create({
                            'name': buyer_full_name,
                            'ref': "TP%s" % (data['buyer']['id']),
                            'customer': True,
                            'email': datas_single['buyer_info']['buyer_email'],
                            'mobile': datas_single['buyer_info']['buyer_phone']
                        })
                        order_lines = datas_single['order_info']['order_detail']
                        sale_order_line = []
                        for line in order_lines:
                            product = self.env['product.product'].search([('default_code', '=', line['sku'])], limit=1)
                            if not product:
                                product = self.env['product.product'].create({
                                    'name': line['product_name'],
                                    'default_code': line['sku'],
                                    'type': 'product'
                                })
                            # if len(product) > 1:
                            #     raise UserError('Product dengan nama %s dan kode %s lebih dari 1'%(product.name, product.default_code))

                            sale_order_line.append((0, 0 ,{
                                'tp_order_detail_id': line['order_detail_id'],
                                'product_id': product.id,
                                'product_uom_qty': int(line['quantity']),
                                'price_unit': int(line['product_price'])
                            }))
                        
                        vals = {
                            'tp_id': rec.tp_conn_id.id,
                            # 'note': json.dumps(datas_single, indent=2),
                            'tp_order_status': datas_single['order_status'],
                            'tp_order_id': datas_single['order_id'],
                            'tp_fs_id': str(rec.tp_conn_id.app_id),
                            'tp_seller_id': datas_single['seller_id'],
                            'tp_shop_id': datas_single['shop_info']['shop_id'],
                            'tp_shop_name': datas_single['shop_info']['shop_name'],
                            'tp_shop_domain': datas_single['shop_info']['shop_domain'],
                            'tp_shop_owner_email': datas_single['shop_info']['shop_owner_email'],
                            # 'tp_buyer_id': datas_single['buyer_info']['buyer_id'],
                            # 'tp_buyer_fullname': datas_single['buyer_info']['buyer_fullname'],
                            # 'tp_buyer_email': datas_single['buyer_info']['buyer_email'],
                            # 'tp_buyer_phone': datas_single['buyer_info']['buyer_phone'],
                            'client_order_ref': datas_single['invoice_number'],
                            'tp_invoice_number': datas_single['invoice_number'],
                            'tp_invoice_url': datas_single['invoice_url'],
                            'tp_voucher_code': datas_single['payment_info']['voucher_code'],
                            # 'tp_discount_amount': datas_single['payment_info']['discount_amount'],
                            'tp_payment_date': datas_single['payment_info']['payment_date'],
                            'tp_payment_number': datas_single['payment_info']['payment_ref_num'],
                            'tp_payment_status': datas_single['payment_info']['payment_status'],
                            # 'tp_logistic': '%s - %s' % (datas_single['order_info']['shipping_info']['logistic_name'], datas_single['order_info']['shipping_info']['logistic_service']),
                            'logistic_id' : logistic_id,
                            # 'logistic' : logistic_name if logistic_name in ['GoSend','SiCepat'] else False,
                            'confirmation_date': self.get_utc_datetime(datas_single['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time')),
                            'date_order': self.get_utc_datetime(datas_single['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time')),
                            'partner_id': customer_order_id.id,
                            'order_line': sale_order_line,
                        }

                        if datas_single['cancel_request_info']:
                            vals['tp_cancel_request_create_time'] = self.get_utc_datetime(datas_single['cancel_request_info']['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time'))
                            vals['tp_cancel_request_reason'] = datas_single['cancel_request_info']['reason']
                            vals['tp_cancel_request_status'] = datas_single['cancel_request_info']['status']

                        create_sale_order = self.env['sale.order'].create(vals)

                        # detail_shop_obj = self.env['tokopedia.shop.detail'].search([('invoice_number', '=', datas_single['invoice_number'])])
                        # if not detail_shop_obj:
                        #     detail_shop_obj.create({
                        #         'partner_id'    : customer_order_id.id,
                        #         'invoice_number': datas_single['invoice_number'],
                        #         'buyer_fullname': datas_single['buyer_info']['buyer_fullname'] if datas_single['buyer_info']['buyer_fullname'] else data['buyer']['id'],
                        #         'invoice_url'   : datas_single['invoice_url'],
                        #         'comment'       : datas_single['comment'],
                        #         'sale_id'       : create_sale_order.id,
                        #         'logistic'      : '%s - %s' % (datas_single['order_info']['shipping_info']['logistic_name'], datas_single['order_info']['shipping_info']['logistic_service']),
                        #         'date_order'    : self.get_utc_datetime(datas_single['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time')),    
                        #         'tokopedia_shop_id': rec.id
                        #     })
                        if datas_single['order_status'] in [200, 220, 221, 400, 450, 500, 501, 520, 530, 540, 600, 601, 690, 691, 695, 698, 699, 700, 701]:
                            create_sale_order.shipping_label_download()
                            create_sale_order.get_buyer_info()
                            # self._cr.commit()
                            # self._cr.close()
                            # create_sale_order.get_bundling()
                            create_sale_order.action_confirm()
                            # Create Picking
                            # imediate_obj = self.env['stock.immediate.transfer']
                            # for picking in create_sale_order.picking_ids:
                            #     picking.action_confirm()
                            #     picking.action_assign()
                            #     imediate_rec = imediate_obj.create({'pick_ids': [(4, create_sale_order.picking_ids.id)]})
                            #     imediate_rec.process()
                            # Create Invoice
                            create_sale_order.action_invoice_create()
                            self._cr.commit()
                            # for invoice in create_sale_order.invoice_ids:
                            #     invoice.action_invoice_open()
        
    @api.one
    def action_open_detail(self):
        action = self.env.ref('tokopedia_connector.tokopedia_shop_form').read()[0]
        action['res_id'] = self.id
        return action

    @api.depends('tokopedia_shop_line_ids')
    def _compute_total_inv(self):
        for rec in self:
            rec.total_inv = len(rec.tokopedia_shop_line_ids.mapped('invoice_number'))

class TokopediaShopDetail(models.Model):
    _name = 'tokopedia.shop.detail'
    _order = "date_order"

    invoice_number = fields.Char(string='Invoice')
    invoice_url = fields.Char(string='invoice Url')
    comment = fields.Char(string='Comment')
    buyer_fullname = fields.Char(string='Buyer')
    tokopedia_shop_id = fields.Many2one('tokopedia.shop', 'Shop')
    sale_id = fields.Many2one('sale.order', string='Sale')
    partner_id = fields.Many2one('res.partner', string='Customer')
    tp_conn_id = fields.Many2one('tokopedia.connector', string='Connector', related='tokopedia_shop_id.tp_conn_id')
    date_order = fields.Datetime(string="Date Order")
    logistic = fields.Char(string='Logistic')
    tp_order_status = fields.Selection(ORDER_STATUS, related='sale_id.tp_order_status', store=True)
