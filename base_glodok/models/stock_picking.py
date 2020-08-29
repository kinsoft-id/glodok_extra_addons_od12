# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
	_inherit = 'stock.picking'


	direct_pickup = fields.Boolean(string="PickUp By Customer", default=False)
	validated_invoice_list = fields.Char(string="Invoice List", compute="_compute_validated_invoice_list")
	state = fields.Selection([
		('draft', 'Draft'),
		('waiting', 'Waiting Another Operation'),
		('confirmed', 'Waiting'),
		('assigned', 'Ready'),
		('printed','Printed'),
		('done', 'Done'),
		('cancel', 'Cancelled')
		
	], string='Status',
		help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
			 " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
			 " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
			 " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
			 " * Printed: Delivery Slip printed and ready to Push into Batch Picking for delivery.\n"
			 " * Done: has been processed, can't be modified or cancelled anymore.\n"
			 " * Cancelled: has been cancelled, can't be confirmed anymore.")
	partner_region_city_id = fields.Many2one('region',string="Partner City/Region", related="partner_id.region_city_id")
	show_btn_print_slip = fields.Boolean("Show Print Slip", compute="_compute_show_btn_print_slip")


	delivery_status = fields.Selection([('received','Received'),('has_return','Has Return'), ('failed','Failed')], string="Delivery Status")


	batch_state = fields.Selection(string="Batch State", related="batch_id.state", readonly=True)
	batch_user_id = fields.Many2one('res.users', string="Courier", related="batch_id.user_id", readonly=True)

	@api.onchange('direct_pickup')
	def onchange_direct_pickup(self):
		if self.direct_pickup==True:
			if self.batch_id.id:
				return {
					'warning':{
						'title':_('Tidak Valid!'),
						'message':_('Picking ini terkait dengan Memo%s. Tidak dapat PickUp Langsung!' % (self.batch_id.name,))
					},
					'value':{
						'direct_pickup':False
					}
				}

	@api.multi
	def action_cancel(self):
		printed_batched = self.filtered(lambda r:r.state=='printed' and r.batch_id.id!=False)

		if len(printed_batched) and self._context.get('batch_action',False)==False:
			raise ValidationError("Tidak bisa cancel surat jalan berikut ini dikarenakan sudah ditarik ke dalam memo pengiriman!\nMohon Cek:\n%s" % (",".join(printed_batched.mapped('name'),)))

		super(StockPicking, self).action_cancel()

	def set_as_draft(self):
		self.ensure_one()
		if self.state=='cancel':
			self.write({'state':'draft'})
			self.move_lines.write({'state':'draft'})

	def _compute_validated_invoice_list(self):
		for rec in self:
			rec.validated_invoice_list = ", ".join(rec.group_id.sale_id.invoice_ids.filtered(lambda r:r.state not in ['draft','cancel']).mapped('number'))

	def _compute_show_btn_print_slip(self):
		for rec in self:
			done = []
			if rec.state in ['assigned','printed']:
				for move in rec.move_lines:
					if move.product_uom_qty==move.quantity_done:
						done.append(True)
					else:
						done.append(False)
				rec.show_btn_print_slip = all(done)
			else:
				rec.show_btn_print_slip = False

	def all_ok(self):
		self.ensure_one()

		for move in self.move_lines:
			move.set_reserved_done()
			move.set_non_reserved_to_external()

	def check_no_view_location(self):
		for rec in self:
			if rec.picking_type_code=='outgoing':
				for mvl in rec.move_line_ids:
					if mvl.location_id.usage=='view':
						raise ValidationError("Jika External Pilih Lokasi External!")
		
	@api.multi
	def print_slip(self):

		# make sure non reserved has external pickup partner
		ext_loc = self.env.ref('stock.warehouse0').external_loc
		move_line_ext = self.move_line_ids.filtered(lambda r:r.location_id.id==ext_loc.id)
		found_no_external_partner = move_line_ext.filtered(lambda r:r.external_pickup_partner.id==False)
		if len(found_no_external_partner)>0:
			msgs = []
			for ff in found_no_external_partner:
				msgs.append(_("Mohon cek item %s diambil dari %s belum di definisikan Supplier nya!" % (ff.product_id.name, ff.location_id.display_name)))
			raise ValidationError("\n".join(msgs))

		self.check_no_view_location()


		if self.state=='assigned':
			self.write({'state':'printed'})
		
		res = self.env.ref('stock.action_report_delivery').report_action(self)
		
		return res

	def create_batch_per_region(self):
		# _logger.critical(self)
		pick_batched = self.filtered(lambda r:r.batch_id.id!=False)

		if len(pick_batched)>0:
			msgs = _('Can\'t create process pick wich already batched')
			msgs += '\n%s' % (",".join(pick_batched.mapped('name')))
			# _logger.error(msgs)
			raise ValidationError(msgs)

		regions = self.mapped(lambda r:r.partner_id.region_city_id)

		batches = self.env['stock.picking.batch']
		for region in regions:
			# create batch by region
			picking_batch_data = self.filtered(lambda r:r.partner_id.region_city_id.id==region.id).prepare_batch_region(region)
			batches += self.env['stock.picking.batch'].create(picking_batch_data)

		return batches

	def create_batch(self):
		# _logger.critical(self)
		pick_batched = self.filtered(lambda r:r.batch_id.id!=False)

		if len(pick_batched)>0:
			msgs = _('Can\'t create process pick wich already batched')
			msgs += '\n%s' % (",".join(pick_batched.mapped('name')))
			# _logger.error(msgs)
			raise ValidationError(msgs)

		regions = self.mapped(lambda r:r.partner_id.region_city_id)
		picking_batch_data = self.prepare_batch()
		batches = self.env['stock.picking.batch'].create(picking_batch_data)

		return batches


	def prepare_batch_region(self,region):
		user = self._context.get('courier_user', self.env['res.users'])

		datas = {
			'picking_ids':[(6,0, self.ids)],
			'user_id':user.id
		}
		return datas

	def prepare_batch(self):
		user = self._context.get('courier_user', self.env['res.users'])

		datas = {
			'picking_ids':[(6,0, self.ids)],
			'user_id':user.id
		}
		return datas

	@api.multi
	def force_assign(self):
		# check if need external supplier then external supplier must filled
		move_line_need_supplier = self.move_line_ids.filtered(lambda r:r.external_pickup_partner_required==True and r.external_pickup_partner.id==False)
		if len(move_line_need_supplier)>0:
			msgs = ['Mohon cek suplier untuk permintaan item:\n']
			msgs += move_line_need_supplier.mapped(lambda r:"%s (%s %s) belum di definisikan supplier nya!" % (r.product_id.display_name, r.qty_done, r.product_uom_id.name))
			raise ValidationError("\n".join(msgs))
		return super(StockPicking, self).force_assign()


	def received(self):
		self.ensure_one()

		# if any pickup_qty == 0 and location is external
		find_external_pickup_failed = self.move_line_ids.filtered(lambda r:r.location_id.id==self.env.ref('stock.warehouse0').external_loc.id and r.pickup_qty==0)
		if len(find_external_pickup_failed)>0:
			raise ValidationError(_('Terdapat External PickUp yang tidak berhasil diambil! Tidak bisa mengubah menjadi receive!'))
		# check if not has return on picking
		# find stock.picking.batch.has.return
		has_return = self.env['stock.picking.batch.has.return'].search([('picking_id','=',self.id), ('batch_id','=',self.batch_id.id)])
		if has_return:
			has_return.unlink()
		self.delivery_status = 'received'

	def failed(self):
		self.ensure_one()
		self.delivery_status = 'failed'
		data = {}
		data['delivery_status'] = 'has_return'
		data['batch_id'] = self.batch_id.id
		data['picking_id'] = self.id
		data['picking_name'] = self.name
		data['partner_id'] = self.partner_id.id


		# line_ids
		line_ids = []
		for line in self.move_line_ids:
			line_ids.append((0,0,{'move_line_id':line.id, 'qty_received':0.0, 'qty':line.qty_done}))
		data['line_ids'] = line_ids
		# end
		self.env['stock.picking.batch.has.return'].create(data)
		


	def delivery_failed(self):
		self.delivery_status = 'failed'
		picking.action_cancel()

	def has_return(self):
		self.ensure_one()
		# find wizard
		wizard_o = self.env['stock.picking.batch.has.return']
		wizard = wizard_o.search([('picking_id','=',self.id), ('batch_id','=',self.batch_id.id)], limit=1).sorted('id',reverse=True)

		if len(wizard)==1:
			wizard.write({'delivery_status':'has_return'})
		elif len(wizard)>1:
			wiz_sorted = wizard.sorted('id')
			wiz_sorted[0].unlink()

		form = self.env.ref('base_glodok.stock_picking_batch_has_return_form')
		context = dict(self.env.context or {})
		context['default_delivery_status'] = 'has_return'
		context['default_batch_id'] = self.batch_id.id
		context['default_picking_id'] = self.id
		context['default_picking_name'] = self.name
		context['default_partner_id'] = self.partner_id.id


		# default_line_ids
		default_line_ids = []
		for line in self.move_line_ids:
			default_line_ids.append((0,0,{'move_line_id':line.id, 'qty_received':0.0, 'qty':line.qty_done}))
		context['default_line_ids'] = default_line_ids
		# end
		res = {
			'name': "%s" % (_('Pickup Validation')),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.picking.batch.has.return',
			'view_id': form.id,
			'type': 'ir.actions.act_window',
			'context': context,
			'target': 'new',
			'res_id':wizard.id
		}
		return res

	@api.multi
	@api.depends('state', 'is_locked')
	def _compute_show_validate(self):
		# printed = self.filtered(lambda r:r.state=='printed')
		# non_printed = self.filtered(lambda r:r.state!='printed')
		# super(StockPicking, non_printed)._compute_show_validate()
		# for picking in printed:
		# 	picking.show_validate = True
		# if do
		# if non do
		for picking in self:
			if picking.picking_type_code=='outgoing':
				# _logger.critical((picking.state))
				if self._context.get('planned_picking') and picking.state == 'draft':
					picking.show_validate = False
				elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned','printed') or not picking.is_locked:
					picking.show_validate = False
				elif picking.state in ['printed']:
					if picking.direct_pickup == True:
						picking.show_validate = True
					else:
						picking.show_validate = False
				else:
					picking.show_validate = True
			else:
				if self._context.get('planned_picking') and picking.state == 'draft':
					picking.show_validate = False
				elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'printed') or not picking.is_locked:
					picking.show_validate = False
				else:
					picking.show_validate = True

	def check_qty_done(self):

		for rec in self:
			# move_lines
			# must have move_line_ids
			for mv in rec.move_lines:
				if len(mv.move_line_ids)==0:
					raise ValidationError("%s belum di definisikan penerimaannya!" % (mv.product_id.display_name,))

			qty_done_zeros = self.env['stock.move.line']
			# move_line_ids
			for line in rec.move_line_ids:
				if line.product_uom_qty<line.qty_done:
					raise ValidationError("%s Qty yang di receive lebih besar!\n" % (line.product_id.display_name,))
				#elif line.qty_done==0:
				#	qty_done_zeros|=line


			if len(qty_done_zeros)>0:
				raise ValidationError("Mohon isi Qty Done:\n%s" % ("\n".join(qty_done_zeros.mapped(lambda r:r.product_id.display_name))))



	@api.multi
	def button_validate(self):
		do_pickings = self.filtered(lambda r:r.picking_type_code=='outgoing')
		for picking in do_pickings:
			if picking.direct_pickup==False and picking.state=='printed':
				raise ValidationError(_('Tidak bisa validate SJ pada state PRINTED!\nSilahkan definisikan PickUp By Customer Jika ingin validasi dari SJ yang berstatus PRINTED.'))
			elif picking.state=='assigned' and picking.direct_pickup==False:
				if picking.direct_pickup==False:
					picking.direct_pickup = True #set true when user validate when state==assigned
			elif picking.direct_pickup==True and picking.state=='printed' and picking.batch_id.id:
				raise ValidationError(_("Tidak Bisa memvalidasi DO yang sudah ditarik ke memo!"))

		incoming = self.filtered(lambda r:r.picking_type_code=='incoming')
		if len(incoming):
			incoming.check_qty_done()

		# raise ValidationError("EEE")
		return super(StockPicking, self).button_validate()

	@api.multi
	def button_validate_incoming(self):
		return self.button_validate()


	@api.multi
	def button_validate_internal(self):
		return self.button_validate()

	def action_immediate_transfer_wizard(self):
		view = self.env.ref('stock.view_immediate_transfer')
		wiz = self.env['stock.immediate.transfer'].create(
			{'pick_ids': [(4, p.id) for p in self]})
		return {
			'name': _('Immediate Transfer?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.immediate.transfer',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': self.env.context,
		}
