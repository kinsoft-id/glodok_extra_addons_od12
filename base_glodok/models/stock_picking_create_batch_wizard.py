# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


class StockPickingCreateBatchWizard(models.TransientModel):
	_name = 'stock.picking.create.batch.wizard'
	_description = 'Stock Picking Create Batch Wizard'

	region_ids = fields.Many2many('region','stock_picking_create_batch_wizard_region_rel','wizard_id','region_id',string="Delivery Region/Area", required=True)
	
	user_id = fields.Many2one('res.users',string="Courier", required=False)
	picking_out_ids = fields.Many2many('stock.picking', 'stock_picking_create_batch_wizard_picking_rel', 'wizard_id', 'picking_id', string="D.O Ids")



	def _default_available_region_ids(self):
		pickings = self.env['stock.picking'].search([('state','=','printed'),('batch_id','=',False),('picking_type_code','=','outgoing')])
		return pickings.mapped(lambda r:r.partner_region_city_id)

	available_region_ids = fields.One2many('region',compute="_compute_available_region_ids", default=_default_available_region_ids)

	def _compute_available_region_ids(self):
		default = self._default_available_region_ids()

		for rec in self:
			rec.available_region_ids = default

	def _default_available_delivery_man_ids(self):
		delivery_group = self.env.ref('base_glodok.group_delivery_man')
		delivery_mans = delivery_group.users
		return delivery_mans

	available_delivery_man_ids = fields.One2many('res.users',string="Available Delivery Man", default=_default_available_delivery_man_ids, compute="_compute_available_delivery_man_ids")
	@api.multi
	def _compute_available_delivery_man_ids(self):
		delivery_mans = self._default_available_delivery_man_ids()
		for rec in self:
			rec.available_delivery_man_ids = delivery_mans

	@api.onchange('region_ids')
	def onchange_region_ids(self):
		# find out picking who ready not batched
		# _logger.critical((self.region_ids))
		outs = self.env['stock.picking'].search([('state','in',['printed']), ('picking_type_code','=','outgoing'), ('batch_id','=',False), ('partner_region_city_id','in',self.region_ids.ids)])
		self.picking_out_ids = [(6,0,outs.ids)]

	def check_done_not_equal_with_demand(self):
		self.ensure_one()

		errors = []
		for pick in self.picking_out_ids:
			for move in pick.move_lines:
				if move.product_uom_qty!=move.quantity_done:
					params = (move.picking_id.partner_id.name, move.picking_id.name, move.product_id.name, )
					errors.append("- Permintaan \"%s\" pada dokumen \"%s\" untuk Product \"%s\"" % params)

		if len(errors):
			raise ValidationError("Ada permintaan yang belum lengkap, harap di cek:\n%s" % ("\n".join(errors)))
			return False
		else:
			return True


	def check_invoice(self):
		self.ensure_one()

		
		no_invoices = self.picking_out_ids.filtered(lambda r:len(r.group_id.sale_id.invoice_ids.filtered(lambda rr:rr.state not in ['draft','cancel']))==0)
		# _logger.critical(no_invoices)
		if len(no_invoices):
			do = no_invoices.mapped(lambda r:"%s [%s]" % (r.name, r.partner_id.name))
			msgs = _("Invoice untuk surat jalan berikut belum valid, mohon di cek kembali:\n- %s" % ("\n- ".join(do),))
			raise ValidationError(msgs)
			
				

	def confirm(self):
		if len(self.picking_out_ids)==0:
			raise UserError(_("No Pick to Process!"))

		self.check_done_not_equal_with_demand()

		self.check_invoice()
		# raise ValidationError("PPP")
		
		batches = self.picking_out_ids.with_context(courier_user=self.user_id).create_batch()

		form = self.env.ref('stock_picking_batch.stock_picking_batch_form')
		tree = self.env.ref('stock_picking_batch.stock_picking_batch_tree')
		view_mode = 'form'

		view = form
		domain = []
		res_ids = []
		res_id = False
		if len(batches)>1:
			# if multi will show tree
			view_mode = 'tree'
			view = tree
			domain = [('id','in',batches.ids)]
			res_ids = batches.ids
		elif len(batches)==1:
			res_id = batches.id

		context = dict(self.env.context or {})
		res = {
			'name': "Delivery PickUp for  %s" % (self.user_id.name),
			'view_type': 'form',
			'view_mode': view_mode,
			'res_model': 'stock.picking.batch',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'context': context,
			'target': 'current',
			'res_id': res_id,
			'res_ids': res_ids,
			'domain': domain
		}
		# _logger.critical((res,view.name))
		# raise ValidationError('EEEE')
		return res
