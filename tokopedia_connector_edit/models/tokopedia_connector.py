from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import requests
from odoo.exceptions import UserError
from base64 import b64encode
import json
from . import sample_data as sd
from . import sale_order as so
from pytz import timezone
import pytz

import logging
_logger = logging.getLogger(__name__)

TOKEN_URL = 'https://accounts.tokopedia.com/token?grant_type=client_credentials'
BASE_URL = 'https://fs.tokopedia.net'

class TokopediaConnector(models.Model):
    _name = 'tokopedia.connector'
    _inherit = ['mail.thread']

    name            = fields.Char(required=True)
    app_id          = fields.Integer('App ID', required=True)
    client_id       = fields.Char('Client ID', required=True)
    client_secret   = fields.Char('Client Secret',required=True)
    access_token    = fields.Char('Access Token')
    expires_at      = fields.Datetime(compute='_get_expires_at')
    expires_in      = fields.Integer()
    token_type      = fields.Char('Token Type', readonly=True)
    order_from_date = fields.Datetime(default=datetime.now())
    order_to_date   = fields.Datetime()
    is_active       = fields.Boolean(default=True)
    is_connected    = fields.Boolean(default=False, copy=False)
    shop_ids        = fields.One2many('tokopedia.shop', 'tp_conn_id', 'Line')
    whitelist_ids   = fields.One2many('tokopedia.ip.whitelist', 'tp_conn_id', 'White List Line')
    result_message_sync_order = fields.Text()
    state_order     = fields.Selection(so.ORDER_STATUS, string='State Order', default=700)

    # @api.onchange('order_from_date')
    # def _onchange_order_from_date(self):
    #     if self.order_from_date:
    #         date_to = (datetime.strptime(str(self.order_from_date), "%Y-%m-%d %H:%M:%S") + timedelta(hours=23) + timedelta(minutes=59))
    #         self.order_to_date = date_to

    @api.depends('expires_in')
    def _get_expires_at(self, **kwargs):
        for rec in self:
            if rec.expires_in:
                expires_at = datetime.now() + timedelta(seconds=rec.expires_in)
                rec.expires_at = expires_at.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                # if datetime.now() > expires_at and rec.is_active:
                #     rec.change_state_connect()

    def change_state_connect(self):
        for rec in self:
            rec.is_connect = False

    @api.multi
    def get_token(self):
        try:
            r = requests.post(TOKEN_URL, headers={
                'Authorization': 'Basic %s' % (b64encode(('%s:%s' % (self.client_id, self.client_secret)).encode('utf-8')).decode('utf-8')),
                'Content-Length': '0',
                'User-Agent': 'PostmanRuntime/7.26.1',
            })
            token_data = r.json() if r.status_code == 200 else {}

            if token_data.get('access_token') and token_data.get('token_type'):
                self.access_token = token_data.get('access_token')
                self.token_type = token_data.get('token_type')
                self.expires_in = token_data.get('expires_in')
                self.is_connected = True
            # rec.message_post(body="%s" % (token_data))
        except Exception as e:
            _logger.warn(e)
            raise UserError(e)

    @api.multi
    def button_sync_shop(self):
        _logger.debug('button_sync_shop')
        for rec in self:
            # date_from = str(datetime.now().date()) + ' 00:00:00'
            # date_to   = str(datetime.now().date()) +' 23:59:59'
            
            if self.env.user.tz:
                tz = pytz.timezone(self.env.user.tz)
            else:
                tz = pytz.utc
            c_time = datetime.now(tz)
            sdate = c_time.strftime("%Y-%m-%d 00:00:00")
            edate = c_time.strftime("%Y-%m-%d 23:58:59")
            date_from = (datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S') - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            date_to = (datetime.strptime(edate, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
            if rec.app_id and rec.token_type and rec.access_token:
                try:
                    shop_info_url = "%s/v1/shop/fs/%s/shop-info" % (BASE_URL, rec.app_id)
                    Auth = '%s %s' % (self.token_type, self.access_token)
                    headers = {'Authorization': Auth}
                    r = requests.get(shop_info_url, headers=headers)
                    r.raise_for_status()    
                    response = json.loads(r.text)
                    data = response.get('data')
                    if data:
                        for sd in data:
                            shop_id = rec.shop_ids.filtered(lambda x: x.shop_id == sd.get('shop_id'))
                            if shop_id:
                                shop_id.write({
                                    'shop_name': sd.get('shop_name'),
                                    'shop_url': sd.get('shop_url'),
                                    'shop_id': sd.get('shop_id'),
                                    'user_id': sd.get('user_id'),
                                    'province_name': sd.get('province_name'),
                                    'date_shop_created': sd.get('date_shop_created')
                                })
                            else:
                                self.env['tokopedia.shop'].create({
                                    'tp_conn_id': rec.id,
                                    'shop_name': sd.get('shop_name'),
                                    'shop_url': sd.get('shop_url'),
                                    'shop_id': sd.get('shop_id'),
                                    'user_id': sd.get('user_id'),
                                    'province_name': sd.get('province_name'),
                                    'date_shop_created': sd.get('date_shop_created')
                                })
                        ctx = self.env.context
                        _logger.warn('-----context-----')
                        _logger.warn('-----TES-----')
                        _logger.warn(ctx)
                        for shp in rec.shop_ids:
                            if ctx.get('date_from') and ctx.get('date_to'):
                                shp.get_order(ctx.get('date_from', False), ctx.get('date_to', False))
                            else:
                                _logger.warn(date_from)
                                _logger.warn(date_to)
                                shp.get_order(date_from, date_to)

                except Exception as ex:
                    _logger.warn(ex)
                    response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
                    _logger.error(response)
                    message = "Failed get IP whitelists: %s, response: %s" % (ex, response)
                    rec.message_post(message)
                    # rec.action_disconnect()
                    # rec.get_token()
                    # rec.button_sync_shop()

    @api.multi
    def get_ip_whitelist(self):
        try:
            # Testing
            # self.whitelist_ids = False
            # wld = []
            # data = sd.get_whitelist.get('data')
            # _logger.warn(data)
            # for wl in data['ip_whitelisted']:
            #     wld.append((0, 0, {'name': wl}))
            # self.write({
            #     'whitelist_ids': wld
            # })
            # End Testing

            whitelist_url = "%s/v1/fs/%s/whitelist" % (BASE_URL, self.app_id)
            print(whitelist_url)
            Auth = '%s %s' % (self.token_type, self.access_token)
            headers = {
                'Authorization': Auth
            }
            r = requests.get(whitelist_url, headers=headers)
            r.raise_for_status()
            response = json.loads(r.text)
            data = response.get('data')
            if data:
                self.whitelist_ids = False
                wld = []
                for wl in data['ip_whitelisted']:
                    wld.append((0, 0, {'name': wl}))
                self.write({
                    'whitelist_ids': wld
                })
        except Exception as ex:
            _logger.error(ex)
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
            message = "Failed get IP whitelists: %s, response: %s" % (ex, response)
            raise UserError(_(message))

    @api.multi
    def get_courier(self):
        for rec in self:
            for shop in rec.shop_ids:
                try:
                    # url = "%s/v1/logistic/fs/%s/active-info?shop_id=%s" % (BASE_URL, rec.app_id, shop.shop_id)
                    url = "%s/v2/logistic/fs/%s/info?shop_id=%s" % (BASE_URL, rec.app_id, shop.shop_id)
                    Auth = '%s %s' % (rec.token_type, rec.access_token)
                    headers = {'Authorization': Auth}
                    # print(url)
                    r = requests.get(url, headers=headers)
                    r.raise_for_status()
                    response = json.loads(r.text)
                    data = response.get('data')
                    # print(json.dumps(data, indent=2))
                    for courier in data:
                        logistic_name = courier['shipper_name']
                        print(logistic_name)
                        logistic_obj = self.env['tokopedia.logistic'].search([('name', '=', logistic_name)])
                        if not logistic_obj:
                            logistic_obj = self.env['tokopedia.logistic'].sudo().create({'name':logistic_name})
                except Exception as e:
                    _logger.warn(e)
                    raise UserError(e)
    
    @api.model
    def _cron_generate_token(self):
        try:
            tokped_conn = self.search([('is_connected', '=', True)])
            for tpc in tokped_conn:
                if tpc.order_to_date:
                    # date_from = (datetime.strptime(str(tpc.order_to_date), "%Y-%m-%d %H:%M:%S") + timedelta(minutes=1))
                    # date_to = (datetime.strptime(str(tpc.order_to_date), "%Y-%m-%d %H:%M:%S") + timedelta(hours=23) + timedelta(minutes=59))
                    # date_from = (datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S") - timedelta(days=2))
                    # date_to = (datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S")  + timedelta(minutes=1))
                    # print(date_from)
                    # tpc.write({
                    #     'order_from_date' : date_from,
                    #     'order_to_date'   : date_to,
                    # })
                    tpc.get_token()
        except Exception as ex:
                _logger.warn(ex)

        
    def _cron_tokopedia_order(self):
        tokped_conn = self.search([('is_connected', '=', True)])
        for tpc in tokped_conn:
            try:
                tpc.button_sync_shop()
            except Exception as ex:
                _logger.warn(ex)

    @api.multi
    def action_disconnect(self):
        self.is_active = False
        self.is_connected = False
        self.access_token = False
        self.expires_in = False
        self.expires_at = False