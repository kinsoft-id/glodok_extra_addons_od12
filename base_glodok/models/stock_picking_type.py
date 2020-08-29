# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError,ValidationError
import math
import logging
_logger = logging.getLogger(__name__)



class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	count_printed = fields.Integer(compute='_compute_count_printed')
	count_printed_and_ready = fields.Integer(compute='_compute_count_printed_and_ready')

	def get_action_picking_tree_ready(self):
		if self.code=='outgoing':
			return self.get_action_picking_printed()

		elif self.code=='incoming':
			return self.get_action_picking_printed_and_ready()
		else:
			return self._get_action('stock.action_picking_tree_ready')

	def get_action_picking_tree_do_ready(self):
		return self._get_action('stock.action_picking_tree_ready')



	def get_action_picking_printed(self):
		return self._get_action('base_glodok.action_picking_tree_printed')
		
	def get_action_picking_printed_and_ready(self):
		return self._get_action('base_glodok.action_picking_tree_printed_and_ready')

	def _compute_count_printed_and_ready(self):
		# TDE TODO count picking can be done using previous two
		domains = {
			'count_printed_and_ready': [('state', 'in', ['printed','ready'])],
		}
		
		for rec in self:
			
			if rec.name.lower()=='receipts':
				query = """SELECT 
					id, 
					(SELECT COUNT(id) FROM stock_picking where picking_type_id=%s AND state in ('printed','assigned')) AS res
					FROM stock_picking_type
					WHERE id=%s
					"""
				

				params = (rec.id, rec.id)
				
				self.env.cr.execute(query, params)
				results = self.env.cr.dictfetchall()
				
				
				rec.count_printed_and_ready = results[0].get('res')
			else:
				rec.count_printed_and_ready = 0

	def _compute_count_printed(self):
		# TDE TODO count picking can be done using previous two
		domains = {
			'count_printed': [('state', '=', 'printed')],
		}
		
		for rec in self:
			if rec.name.lower()=='delivery orders':
				query = """SELECT 
					id, 
					(SELECT COUNT(id) FROM stock_picking where picking_type_id=%s AND batch_id IS NULL AND state ='printed') AS printed
					FROM stock_picking_type
					WHERE id=%s
					"""

				params = (rec.id, rec.id)
				self.env.cr.execute(query, params)
				results = self.env.cr.dictfetchall()
				
				rec.count_printed = results[0].get('printed')
			else:
				rec.count_printed = 0

