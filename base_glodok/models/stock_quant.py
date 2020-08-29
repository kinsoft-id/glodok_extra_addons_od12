# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	@api.model
	def _get_removal_strategy_order(self, removal_strategy):
		if removal_strategy == 'fifo':
			# return 'location_id ASC, in_date ASC NULLS FIRST, id'
			return """
				CASE location_id
					WHEN 19 then 1
					WHEN 18 then 2
					WHEN 20 then 3
					WHEN 21 then 4
					WHEN 21 then 5
					ELSE 6
				end, in_date ASC NULLS FIRST, id"""
		elif removal_strategy == 'lifo':
			return 'in_date DESC NULLS LAST, id desc'
		raise UserError(_('Removal strategy %s not implemented.') % (removal_strategy,))