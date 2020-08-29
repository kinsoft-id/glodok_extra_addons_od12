# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	taken_qty = fields.Float(string="Taken Qty")
	taken_move_line_ids = fields.One2many('stock.move.line', 'took_purchase_line_id',string="Taken Move Lines")