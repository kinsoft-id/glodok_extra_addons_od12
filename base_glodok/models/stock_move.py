# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
	_inherit = 'stock.move'

	def set_reserved_done(self):
		for rec in self.filtered(lambda r:r.reserved_availability>0):
			if len(rec.move_line_ids)>0:
				for line in rec.move_line_ids:
					line.qty_done = line.product_uom_qty #set done same as reserved qty in move.line object

			else:
				# if no move line but only move
				if rec.reserved_availability>0:
					rec.quantity_done = rec.reserved_availability

	def set_non_reserved_to_external(self):
		self.ensure_one()
		if self.product_uom_qty!=self.reserved_availability:
			
			diff_qty = self.product_uom_qty-self.quantity_done-self.reserved_availability
			if diff_qty>0:
				if self.reserved_availability>0:
					diff_qty += self.reserved_availability
				move_line_data = {
					'location_id':self.env.ref('stock.warehouse0').external_loc.id,
					'qty_done':diff_qty,
					'move_id': self.id,
		            'product_id': self.product_id.id,
		            'product_uom_id': self.product_uom.id,
		            'location_dest_id': self.location_dest_id.id,
		            'picking_id': self.picking_id.id,
				}
				self.move_line_ids = [(0,0,move_line_data)]
		return self.action_show_details()