from odoo import api, fields, models, _
import time
import base64
import odoo.tools

import logging
_logger = logging.getLogger(__name__)


class export_customer_invoice_wizard(models.TransientModel):
    _name = 'export.customer.invoice.wizard'

    tmp_dir = '/tmp/'
    
    date_from = fields.Date("Date From", required=True, default=fields.Datetime.now )
    date_to = fields.Date("Date To", required=True, default=fields.Datetime.now )
    user_id = fields.Many2one('res.users', string='Salesperson')
    is_shopee25 = fields.Boolean(string="Is Shopee 2.5?",  )
    is_blibli25 = fields.Boolean(string="Is Blibli 2.5?",  )

    export_file = fields.Binary(string="Export File",  )
    export_filename = fields.Char(string="Export File",  )


    total_records = fields.Integer("Total Records", readonly=True)
    total_durations = fields.Float("Duration (s)", readonly=True)

   
    @api.multi
    def confirm_button(self):
        start = time.time()

        cr = self.env.cr

        sh = "0 AS Shopee,"
        jawir = """(CASE WHEN ai.name NOT LIKE '%COD%' AND ai.name NOT LIKE '%cod%' 
                    THEN 1 ELSE 0 END) AS Jawir,"""
        if self.is_shopee25:
            sh = "(CASE WHEN ai.name LIKE 'SH%' THEN 2.5 WHEN ai.name LIKE 'sh%' THEN 2.5 ELSE 0 END) AS Shopee,";
            jawir = """(CASE WHEN ai.name NOT LIKE 'SH%' AND ai.name NOT LIKE 'sh%'
                    AND ai.name NOT LIKE '%COD%' 
                    AND ai.name NOT LIKE '%cod%' 
                    THEN 1 ELSE 0 END) AS Jawir,"""

        if self.is_blibli25:
            sh = "(CASE WHEN ai.name LIKE 'BLI%' THEN 2.5 WHEN ai.name LIKE 'Bli%' THEN 2.5 " \
                 "WHEN ai.name LIKE 'bli%' THEN 2.5 ELSE 0 END) AS Shopee,";
            jawir = """(CASE WHEN ai.name NOT LIKE 'BLI%' AND ai.name NOT LIKE 'Bli%'
                    AND ai.name NOT LIKE 'bli%'
                    AND ai.name NOT LIKE '%COD%' 
                    AND ai.name NOT LIKE '%cod%' 
                    THEN 1 ELSE 0 END) AS Jawir,"""

        sql = """\COPY (
                SELECT rp.name AS Customer, ai.date AS Invoice_Date, ai.number AS Invoice_NUmber, 
                 ai.name AS Reference,
                 ru.login AS salesperson, ai.date_due AS Due_Date, ai.origin AS Source_Document,
                 amount_total_signed AS Total, residual_signed AS Amount_Due, state AS Status,
                 """ + sh + """ 
                 """ + jawir + """ 
                 '' AS Toko, 
                 SUM(CASE WHEN ai.name LIKE '%COD%' AND ail.price_unit >= 1000000 THEN quantity
                    WHEN ai.name LIKE '%cod%' AND ail.price_unit >= 1000000 THEN quantity ELSE 0 END) AS Qty_gt_1_jt, 
                 SUM(CASE WHEN ai.name LIKE '%COD%' AND ail.price_unit < 1000000 AND ail.price_unit > 0 THEN quantity 
					WHEN ai.name LIKE '%cod%' AND ail.price_unit < 1000000 AND ail.price_unit > 0 THEN quantity ELSE 0 END) AS Qty_lt_1_jt
                FROM account_invoice ai 
                JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                JOIN res_partner rp ON ai.partner_id = rp.id
                JOIN res_users ru ON ai.user_id = ru.id
                JOIN product_product pp ON ail.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE ai.type = 'out_invoice'
                AND ai.state IN ('open','paid')
                AND ai.name NOT IN ('COD DESY','cod desy','COD ENGKO','cod engko','COD NGKO','cod ngko','COD ENCI','cod enci','COD NCI','cod nci','COD HENRI','cod henri')
                AND ail.product_id NOT IN (6416, 6604)
                AND pt.type IN ('product','consu')
                AND ai.user_id = """ + str(self.user_id.id) + """
                AND ai.date BETWEEN '""" + self.date_from + """' AND '""" + self.date_to + """'
                GROUP BY ai.id, rp.name, ai.date, ai.number, 
                 ai.name,
                 ru.login, ai.date_due, ai.origin,
                 ai.amount_total_signed, ai.residual_signed, ai.state
                ORDER BY ai.date DESC
            ) TO '/tmp/export.csv' WITH (FORMAT CSV, HEADER TRUE, FORCE_QUOTE *)
        """

        #------- psql dgn \copy command
        cmd = ['psql']
        cmd.append('--command='+sql)
        cmd.append( cr.dbname )
        odoo.tools.exec_pg_command(*cmd)

        # file terdowbnload ke local forlder odoo : /tmp/namafile
        fo = open('/tmp/export.csv', "rb")
        self.export_file = base64.b64encode( fo.read() )
        fo.close()
        self.export_filename = '/tmp/export.csv'

        end = time.time()
        self.total_durations = end-start         
        return {
            'name': "Export Complete, total %s seconds" % self.total_durations,
            'type': 'ir.actions.act_window',
            'res_model': 'export.customer.invoice.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    