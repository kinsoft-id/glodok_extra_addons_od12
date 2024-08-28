from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'


    escpos_esc = fields.Integer("ESC", default=0x001B)
    escpos_gs = fields.Integer("GS", default=0x001D)

