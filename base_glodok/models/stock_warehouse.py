# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class StockWarehouse(models.Model):
	_inherit = 'stock.warehouse'


	external_loc = fields.Many2one('stock.location', string="External Location")
	default_return_location_id = fields.Many2one('stock.location', string="Default Return Location")