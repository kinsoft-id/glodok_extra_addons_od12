from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class ReportRekap(models.Model):
    _name = 'report.rekap'
    _auto = False

    no_order = fields.Char(string='No Order Pesanan')
    customer_id = fields.Many2one('res.partner', string='Nama Konsumen')
    logistic_id = fields.Many2one('tokopedia.logistic', string='Logistic')
    product_id = fields.Many2one('product.product', string='Nama Barang')
    sku = fields.Char(string='Nama Barang')
    quantity = fields.Float(string='Quantity')
    location_id = fields.Many2one('stock.location', string='Source Location')
    no_resi = fields.Char(string='No Resi')

class ReportRekapWizard(models.TransientModel):
    _name = 'report.rekap.wizard'

    # start_date = fields.Date(string="Start Date", required=True, default=fields.Date.today())
    # end_date = fields.Date(string="End Date", required=True, default=fields.Date.today())
    start_date = fields.Datetime(string="Start Date", required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string="End Date", required=True, default=fields.Datetime.now)
    logistic_id = fields.Many2one('tokopedia.logistic', string='Logistic Name')

    @api.multi
    def action_open_view(self):
        start = self.start_date
        end = self.end_date

        query_where = " "
        if self.logistic_id:
            query_where = " and so.logistic_id = %s " % self.logistic_id.id

        query =  """
            CREATE OR REPLACE VIEW report_rekap AS (
                SELECT row_number() OVER () as id
                , sm.origin as no_order
                , sm.partner_id as customer_id
                , so.logistic_id as logistic_id
                , sm.product_id as product_id
                , pp.default_code as sku
                , sm.product_qty as quantity
                , sm.location_id as location_id
                , sm.reference as no_resi
                from stock_move sm 
                join product_product pp on sm.product_id = pp.id
                join sale_order_line sol on sm.sale_line_id = sol.id
                join sale_order so on sol.order_id = so.id
                WHERE sm.date BETWEEN '%s' AND '%s' %s
        )""" % (start, end, query_where)
        self._cr.execute(query)
        return self.env.ref('report_rekap.report_rekap_action').read()[0]                
        
    @api.multi
    def action_print(self):
        start = self.start_date
        end = self.end_date

        query_where = " "
        if self.logistic_id:
            query_where = " and so.logistic_id = %s " % self.logistic_id.id

        query =  """
            SELECT row_number() OVER () as id
            , sm.origin as no_order
            , sm.partner_id as customer_id
            , rp.name as customer_name
            , so.logistic_id as logistic_id
            , tl.name as logistic_name
            , sm.product_id as product_id
            , pp.default_code as sku
            , sm.product_qty as quantity
            , sm.location_id as location_id
            , sl.name as location_name
            , sm.reference as no_resi
            from stock_move sm 
            join product_product pp on sm.product_id = pp.id
            join sale_order_line sol on sm.sale_line_id = sol.id
            join sale_order so on sol.order_id = so.id
            join res_partner rp on sm.partner_id = rp.id
            join tokopedia_logistic tl on so.logistic_id = tl.id
            join stock_location sl on sm.location_id = sl.id
            WHERE sm.date BETWEEN '%s' AND '%s' %s
        """ % (start, end, query_where)
        self._cr.execute(query)
        record = self._cr.dictfetchall()

        datas = {
            # 'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start'    : self.start_date,
                'date_end'      : self.end_date,
                'record'        : record
            },
        }
        return self.env.ref('report_rekap.report_rekap_id').report_action(self, data=datas)
        # return self.env['report'].get_action(self, 'report_rekap.report_rekap_template')

# class ValueReport(models.AbstractModel):
class ValueReport(models.TransientModel):
    _name = 'report.report_rekap.report_rekap_template'

    # @api.model
    def get_report_values(self, docids, data=None):
        date_start  = data['form']['date_start']
        date_end    = data['form']['date_end']
        record      = data['form']['record']

        return {
            'doc_ids'       : docids,
            'doc_model'     : data['model'],
            'docs'          : record,
            'data'          : data,
            'date_start'    : date_start,
            'date_end'      : date_end,
            }