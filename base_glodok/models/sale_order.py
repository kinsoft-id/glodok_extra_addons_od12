# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit = 'sale.order'


	delivery_slip_printed = fields.Boolean('Delivery Slip Printed',compute="_compute_delivery_slip_printed")
	envelope_print_counter = fields.Integer('Envelope Printed')
	need_follow_up = fields.Boolean('Need Follow Up', default=False)

	def _compute_delivery_slip_printed(self):
		for rec in self:
			pickings = rec.picking_ids.filtered(lambda r:r.state!='cancel')
			printed = pickings.mapped(lambda r:r.state in ['printed','done'])
			if len(printed):
				rec.delivery_slip_printed = all(printed)
			else:
				rec.delivery_slip_printed = False

	def action_print_envelope(self):
		self.ensure_one()
		envelope_print_counter = self.envelope_print_counter+1
		self.envelope_print_counter = envelope_print_counter
		action = self.env['ir.actions.act_window'].for_xml_id('base_glodok', 'sale_order_envelope_report')
		return action
