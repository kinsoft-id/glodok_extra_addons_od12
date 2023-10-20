from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pdfkit
import requests
import base64
import json
from datetime import datetime
import pytz
from . import tokopedia_js as tj

import logging
_logger = logging.getLogger(__name__)

ACK_ORDER_URL = 'https://fs.tokopedia.net/v1/order/%s/fs/%s/ack'
PICKUP_REQUEST_URL = "https://fs.tokopedia.net/inventory/v1/fs/%s/pick-up"
SHIPPING_LABEL_URL = 'https://fs.tokopedia.net/v1/order/%s/fs/%s/shipping-label'
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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tp_order_status = fields.Selection(ORDER_STATUS)
    tp_order_id = fields.Char()
    tp_fs_id = fields.Char()
    tp_id = fields.Many2one('tokopedia.connector')

    tp_seller_id = fields.Char()
    tp_shop_id = fields.Char()
    tp_shop_name = fields.Char()
    tp_shop_domain = fields.Char()
    tp_shop_owner_email = fields.Char()
    tp_shop_owner_phone = fields.Char()

    tp_buyer_id = fields.Char()
    tp_buyer_fullname = fields.Char()
    tp_buyer_email = fields.Char()
    tp_buyer_phone = fields.Char()

    tp_invoice_number = fields.Char(index=True)
    tp_invoice_url = fields.Char()
    tp_invoice_data = fields.Binary()

    tp_payment_number = fields.Char()
    tp_payment_status = fields.Char()
    tp_gateway_name = fields.Char()
    tp_voucher_code = fields.Char()
    tp_discount_amount = fields.Float()
    tp_payment_date = fields.Datetime()

    tp_cancel_request_create_time = fields.Datetime('Create Time')
    tp_cancel_request_reason = fields.Char('Reason')
    tp_cancel_request_status = fields.Integer('Status')
    show_html_text = fields.Boolean()
    tp_text_shipping_html = fields.Text()
    tp_no_resi_shipping = fields.Char()
    
    shipping_label_data = fields.Binary()
    shipping_label_text = fields.Char()
    tp_logistic = fields.Char(string='Logistic Name')
    download_label = fields.Boolean(string='Download Label', default=False)

    # tokopedia_order = fields.Char(compute='_tokopedia_order_status')
    tokopedia_tracking_ids = fields.One2many('tokopedia.tracking', 'order_id', 'Line')

    text_bundling = fields.Text(string='Text Bundling')
    logistic = fields.Selection([("GoSend","GoSend"),("SiCepat","SiCepat")], string='Logistic')
    logistic_id = fields.Many2one('tokopedia.logistic', string='Logistic Name', index=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')

    @api.multi
    def action_multi_download_label(self):
        tab_id = []
        for attachment in self:
            tab_id.append(attachment.attachment_id.id)
        url = '/web/binary/download_label?tab_id=%s' % tab_id
        print(url)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def shipping_label_download(self):
        for rec in self:
            try:
                url = SHIPPING_LABEL_URL % (rec.tp_order_id, rec.tp_id.app_id)
                Auth = '%s %s' % (rec.tp_id.token_type, rec.tp_id.access_token)
                headers = {
                    'Authorization': Auth
                }
                r = requests.get(url, headers=headers)
                r.raise_for_status()
                status_code = r.status_code
                response = r.content
                shipping_label_data = pdfkit.from_string(str(response.decode('UTF-8')))
                encoded_datas = base64.b64encode(shipping_label_data)
                attachment = self.env['ir.attachment'].sudo().create({
                    'name'      : rec.name,
                    'datas'     : encoded_datas,
                    'res_id'    : rec.id,
                    'res_model' : rec._name,
                })
                rec.write({
                    "tp_text_shipping_html" : response,
                    "shipping_label_data"   : encoded_datas,
                    "attachment_id"         : attachment.id,
                    "shipping_label_text"   : "Shipping Label of %s" % (rec.tp_order_id)
                })
            except Exception as ex:
                _logger.error(ex)

    def get_bundling(self):
        try:
            # print('===============BUNDLING===============')
            # single_order_url = '%s/v2/fs/%s/order?invoice_num=%s' % (BASE_URL,self.tp_id.app_id, self.tp_invoice_number)
            # single_order_auth = '%s %s' % (self.tp_id.token_type, self.tp_id.access_token)
            # req_single = requests.get(single_order_url, headers={'Authorization': single_order_auth})
            # response = json.loads(req_single.text)
            # datas_single = response.get('data') if req_single.status_code == 200 else {}
            # order_lines = datas_single['order_info']['order_detail']
            # for line in order_lines:
                # print(line['product_id'])

                # https://fs.tokopedia.net/v1/products/bundle/fs/99999/info?product_id=2147981945
                # /v1/products/bundle/fs/:fs_id/info
                # /v1/products/bundle/fs/:fs_id/list
            url = '%s/v1/products/bundle/fs/%s/list?shop_id=%s&type=1&status=1&last_group_id=' % (BASE_URL, self.tp_fs_id, self.tp_shop_id)
                # url = '%s/v1/products/bundle/fs/%s/list?shop_id=%s&type=1&status=1&product_id=%s' % (BASE_URL, self.tp_fs_id, self.tp_shop_id, line['product_id'])
            Auth = '%s %s' % (self.tp_id.token_type, self.tp_id.access_token)
            req = requests.get(url, headers={'Authorization': Auth})
                # headers = req.headers
                # req.raise_for_status()
                # print(req.text)
            response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}
            data = response.get('data') or False
            print(data)
            self.write({"text_bundling": data})
        except Exception as ex:
            _logger.error(ex)


    def get_buyer_name(self):
        if self.tp_text_shipping_html:
            shipping_text_html = self.tp_text_shipping_html
            # print(shipping_text_html)
            partner_fullname = shipping_text_html.split("Kepada:")
            partner_fullname_2 = partner_fullname[1].split("b>")
            partner_fullname_3 = partner_fullname_2[1].split("</")
            partner_fullname_4 = partner_fullname_3[0]
            partner_fullname_final = ' '.join([vals for vals in partner_fullname_4.split(" ") if vals])
            self.partner_id.write({'name': partner_fullname_final})
            self.write({'tp_buyer_fullname': partner_fullname_final})

    def get_buyer_address(self):
        if self.tp_text_shipping_html:
            shipping_text_html = self.tp_text_shipping_html
            address_and_mobile_split = shipping_text_html.split("Kepada:")
            address_and_mobile_split_2 = address_and_mobile_split[1].split("<br />")
            # print(address_and_mobile_split_2)
            address_dirty = address_and_mobile_split_2[3]
            # print(address_dirty)
            self.partner_id.write({'street': ' '.join([vals for vals in address_dirty.split(" ") if vals])})

    def get_buyer_city(self):
        if self.tp_text_shipping_html:
            shipping_text_html = self.tp_text_shipping_html
            address_and_mobile_split = shipping_text_html.split("Kepada:")
            address_and_mobile_split_2 = address_and_mobile_split[1].split("<br />")
            # print(address_and_mobile_split_2)
            # print("================================")
            address_dirty = address_and_mobile_split_2[3]
            # print(address_dirty)
            # print("================================")
            street = ' '.join([vals for vals in address_dirty.replace("\n", "").split(" ") if vals])
            print(street)
            print("================================")
            city = street.split(", ")
            print(city)
            city2 = city[1].split(".")
            print(city2)

            city3 = ''
            if len(city2) == 2:
                city3 = city2[0]
            if len(city2) == 3:
                city3 = city2[0] + '.' + city2[1]
            
            if city3:
                print(city3)
                city_obj = self.env['region'].search([('name','ilike', city3)], limit=1)
                print(city_obj)
                self.partner_id.write({'region_city_id': city_obj.id})
    
    def get_buyer_district(self):
        if self.tp_text_shipping_html:
            shipping_text_html = self.tp_text_shipping_html
            address_and_mobile_split = shipping_text_html.split("Kepada:")
            address_and_mobile_split_2 = address_and_mobile_split[1].split("<br />")
            # print(address_and_mobile_split_2)
            address_dirty = address_and_mobile_split_2[3]
            street = ' '.join([vals for vals in address_dirty.replace("\n", "").split(" ") if vals])
            city = street.split(", ")
            print(city)
            city2 = city[0].split(".")

            city3 = city2[0].replace("\n", "")
            
            print(city3)
            city_obj = self.env['region'].search([('name','ilike', city3)], limit=1)
            print(city_obj)
            self.partner_id.write({'region_district_id': city_obj.id})
    
    def get_buyer_mobile(self):
        if self.tp_text_shipping_html:
            shipping_text_html = self.tp_text_shipping_html
            address_and_mobile_split = shipping_text_html.split("Kepada:")
            address_and_mobile_split_2 = address_and_mobile_split[1].split("<br />")
            mobile_dirty = address_and_mobile_split_2[4].split("</td>")
            # print(mobile_dirty)
            self.partner_id.write({'mobile': mobile_dirty[0].replace(" ", "")})

    
    def get_buyer_info(self):
        self.get_buyer_name()
        self.get_buyer_address()
        self.get_buyer_city()
        self.get_buyer_district()
        self.get_buyer_mobile()
        

    # @api.one
    def action_view_tracking(self):
        # action = self.env.ref('tokopedia_connector.sale_order_tracking_action').read()[0]
        # action['res_id'] = self.id
        # action['name'] = 'Tracking - %s ' % self.client_order_ref
        # return action
        _logger.warn('action_view_tracking')
        try:
            self.ensure_one()
            # self.tokopedia_tracking_ids = False
            self._cr.execute("""delete from tokopedia_tracking where order_id = %s"""%(self.id))
            single_order_url = '%s/v2/fs/%s/order?invoice_num=%s' % (
                BASE_URL,
                self.tp_id.app_id,
                self.tp_invoice_number
            )
            Auth = '%s %s' % (self.tp_id.token_type, self.tp_id.access_token)
            req = requests.get(single_order_url, headers={
                'Authorization': Auth
            })
            headers = req.headers
            req.raise_for_status()
            response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}
            datas_single = response.get('data') if req.status_code == 200 else {}
            self.tokopedia_tracking_ids = [(0, 0, {
                                        'action_by': t.get('action_by'),
                                        'message': t.get('message'),
                                        'comment': t.get('comment'),
                                        'date': pytz.timezone('Asia/Jakarta').localize(datetime.strptime(t.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(pytz.UTC),
                                    }) for t in datas_single["order_info"]["order_history"]]

            
            action = self.env.ref('tokopedia_connector.sale_order_tracking_action').read()[0]
            action['res_id'] = self.id
            action['name'] = 'Tracking - %s ' % self.client_order_ref
            return action
        except Exception as ex:
            _logger.error(ex)
            raise ValidationError(ex)

    
    def action_download_label(self):
        self.ensure_one()
        if self.download_label:
            raise UserError(_("Label sudah di download."))
        else:
            self.download_label = True
            return {
                'name': 'FEC',
                'type': 'ir.actions.act_url',
                # 'url': '/web/content/?model=sale.order&id={}&field=dummy&filename_field=dummy_filename&download=true'.format(self.id),
                'url': '/web/content/?model=sale.order&id={}&field=shipping_label_data&download=true'.format(self.id),
                'target': 'self',
            }

    def show_ship_label(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        raport_pdf_name = "Tokopedia shipping label for %s" % (self.tp_order_id)
        url = "/api/v1/file/%s/%s/%s" % (
            self._name,
            self.id,
            raport_pdf_name.replace(" ", "%20")
        )
        return {                   
            'name'     : 'Show Ship Label',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : url
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tp_order_detail_id = fields.Float(string="Order Detail ID")

class TokopediaTracking(models.Model):
    _name = 'tokopedia.tracking'

    action_by = fields.Char(string='Action By')
    message = fields.Char(string='Message')
    comment = fields.Char(string='Comment')
    date = fields.Datetime(string='Date')
    order_id = fields.Many2one('sale.order', 'Sale')

class TokopediaLogistic(models.Model):
    _name = 'tokopedia.logistic'

    name = fields.Char(string='Name')