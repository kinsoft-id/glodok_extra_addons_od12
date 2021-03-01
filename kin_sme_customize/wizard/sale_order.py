from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class export_sale_order_wizard(models.TransientModel):
    _name = 'export.sale.order.wizard'

    tmp_dir = '/tmp/'
    
    date_from = fields.Date("Date From", required=True, default=fields.Datetime.now )
    date_to = fields.Date("Date To", required=True, default=fields.Datetime.now )

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        """
        This onchange method is used to check end date should be greater than
        start date.
        """
        if self.date_from and self.date_to and \
                self.date_from > self.date_to:
            raise Warning(_('Date to must be greater than date from'))

    @api.multi
    def get_result(self):
        data = self.read()[0]
        date_from = data.get('date_from', False)
        date_to = data.get('date_to', False)
        if date_from and date_to and date_to < date_from:
            raise Warning(_("Date to should be greater than date from!"))

        where_date_from = " 1=1 "
        if date_from:
            where_date_from = " so.date_order + interval '7 hour' >= '%s 00:00:00' " % date_from
        where_date_to = " 1=1 "
        if date_to:
            where_date_to = " so.date_order + interval '7 hour' <= '%s 23:59:59'" % date_to

        cr = self.env.cr
        sql = """
            SELECT 
                so.date_order, so.name, CONCAT('[', pt.default_code, '] ', pt.name) AS product_name, 
                pu.name AS product_uom, sol.product_uom_qty, sol.margin
            FROM sale_order so
            LEFT JOIN sale_order_line sol ON sol.order_id = so.id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_uom pu ON pu.id = sol.product_uom
            WHERE  so.state = 'done' 
            AND """ + where_date_from + """ 
            AND """ + where_date_to + """
            ORDER BY so.date_order ASC, so.name ASC
        """
        # print(sql)
        list_data = []

        cr.execute(sql)
        vals = cr.fetchall()

        no = 1
        for val in vals:
            subtot_margin = float(val[4]) * float(val[5])
            list_data.append({
                'date_order': val[0],
                'name': val[1],
                'product_name': val[2],
                'product_uom': val[3],
                'product_qty': val[4],
                'margin': val[5],
                'subtot_margin': subtot_margin
            })
            no += 1
        hasil = list_data
        return hasil

    @api.multi
    def confirm_button(self):
        return self.env.ref('kin_sme_customize.laporan_rekap_margin_penjualan').report_action(self)