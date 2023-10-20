from odoo import models, fields, api

class TokopediaIpWhitelist(models.Model):
    _name = 'tokopedia.ip.whitelist'

    name = fields.Char(string='IP')
    tp_conn_id = fields.Many2one('tokopedia.connector', string='Tp Conn')