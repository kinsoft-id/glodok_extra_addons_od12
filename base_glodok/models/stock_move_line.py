# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	picking_partner = fields.Many2one('res.partner', related='picking_id.partner_id', readonly=True)
	picking_origin = fields.Char('Origin', related="picking_id.origin")
	picking_state = fields.Selection('Picking State', related="picking_id.state")
	# pickup_method = fields.Selection([('stock','From Stock'), ('external','External PickUp')], string="PickUp Method", default="stock", required=True)
	external_pickup_partner_required = fields.Boolean(string="External Pickup Partner Required", compute="_compute_external_pickup_partner_required")
	external_pickup_partner = fields.Many2one('res.partner', string="External Supplier", domain=[('supplier','=',True)])

	pickup_validated = fields.Boolean('Pickup Validated', default=False)
	pickup_qty = fields.Float('Pickup Qty')
	pickup_validated_by = fields.Many2one('res.users', string='Pickup Validated By')

	batch_state = fields.Selection(string="Batch State", related="picking_id.batch_state", readonly=True)

	wizard_return_line_ids = fields.One2many('stock.picking.batch.has.return.line', 'move_line_id', string="Wizard Return Lines")

	wizard_return_qty = fields.Float(string="Wizard Return Qty", compute="_copmute_wizard_return_qty")


	pembeli = fields.Char("Pembeli", related='picking_id.partner_id.name')
	batch = fields.Char("Batch", related='picking_id.batch_id.name')
	cust_reference = fields.Char("Customer Reference", related='picking_id.sale_id.client_order_ref')
	salesperson = fields.Char("Salesperson", related='picking_id.sale_id.user_id.name')
	nama_kurir = fields.Char("Nama Kurir", related='picking_id.batch_id.user_id.name')
	is_label_printed = fields.Boolean("Is Label Printed")

	@api.multi
	def button_print_label(self):
		self.write({'is_label_printed': True})

		document = self.env.ref('base_glodok.action_report_label_pengiriman').report_action(self)

		# _logger.critical(document)

		return document

	@api.multi
	def _copmute_wizard_return_qty(self):
		for rec in self:
			rec.wizard_return_qty = sum(rec.wizard_return_line_ids.mapped('qty_received'))



	def update_suppplier_changes(self):
		return {'type': 'ir.actions.act_window_close'}

	def change_supplier(self):
		form = self.env.ref('base_glodok.stock_move_line_change_supplier_form')
		
		context = dict(self.env.context or {})
		context['default_batch_id'] = self.id
		res = {
			'name': "%s" % (_('Change Supplier')),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.move.line',
			'view_id': form.id,
			'type': 'ir.actions.act_window',
			'context': context,
			'target': 'new',
			'res_id':self.id,
		}
		return res

	# took_purchase_line_id = fields.Many2one('purchase.order.line', string="Took From Purchase Order Line")


	# @api.onchange('took_purchase_line_id')
	# def onchange_took_purchase_line_id(self):
	# 	if self.took_purchase_line_id.id:


	def _compute_external_pickup_partner_required(self):
		for rec in self:
			res = False
			# _logger.critical(('EEEEEE', self.env.ref('stock.warehouse0').external_loc.id, self.env.ref('stock.warehouse0').external_loc.id))
			if rec.picking_id.picking_type_id.code=='outgoing':

				if rec.location_id.id==self.env.ref('stock.warehouse0').external_loc.id:
					res = True

			rec.external_pickup_partner_required = res

	# def _set_external_pickup_partner_invisible(self, arch):
	# 	doc = etree.XML(arch)
	# 	for node in doc.xpath("//field[@name='external_pickup_partner']"):
	# 		# _logger.warning(('get node---------->>', node.get('attrs')))
	# 		node.set('invisible','1')
	# 		node.set('required','False')
	# 		# _logger.warning(('get node afterrr---------->>', node.get('invisible')))
	# 	return doc

	# @api.model
	# def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
	# 	sup = super(StockMoveLine, self)._fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
		
	# 	if sup['type'] == 'tree' and sup['model'] == 'stock.move.line' and sup['name'] == 'stock.move.line.operations.tree':
	# 		if self._context.get('')	
	# 		doc = self._set_external_pickup_partner_invisible(sup['arch'])
	# 		sup['arch'] = etree.tostring(doc, encoding='unicode')
	# 	return sup
