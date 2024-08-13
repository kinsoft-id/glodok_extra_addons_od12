# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockPickingBatchReport(models.Model):
	_name = 'stock.picking.batch.report'
	_description = 'Stock Picking Batch Report'


	batch_id =  fields.Many2one('stock.picking.batch', required=True, string="Batch")
	picking_id = fields.Many2one('stock.picking', required=True, string="Picking")
	delivery_status = fields.Selection([('received','Received'), ('has_return','Has Return'), ('failed','Failed')], string='Delivery Status', required=True)
	line_ids = fields.One2many('stock.picking.batch.report.line', 'report_id', string="Lines")
	name = fields.Char(string="Name")

class StockPickingBatchReportLine(models.Model):
	_name = 'stock.picking.batch.report.line'
	_description = 'Stock Picking Batch Report Line'

	report_id = fields.Many2one('stock.picking.batch.report', required=True, string="Report")
	move_line_id = fields.Many2one('stock.move.line', string="Move Line", required=True)
	qty = fields.Float('Qty', related="move_line_id.qty_done", readonly=True, store=True)
	location_id = fields.Many2one('stock.location',string='Location', related="move_line_id.location_id", readonly=True, store=True)
	external_pickup_partner = fields.Many2one('res.partner',string='Supplier', related="move_line_id.external_pickup_partner", readonly=True, store=True)
	qty_received = fields.Float("Qty Received")


class StockPickingBatchHasReturn(models.TransientModel):
	_name = 'stock.picking.batch.has.return'
	_description = 'Stock Picking Batch Has Return'

	batch_id =  fields.Many2one('stock.picking.batch', required=True, string="Batch")
	picking_id = fields.Many2one('stock.picking', required=True, string="Picking")
	partner_id = fields.Many2one('res.partner', string="Customer", related='picking_id.partner_id', readonly=True)
	picking_name = fields.Char(string="Delivery Slip", related='picking_id.name', readonly=True)
	delivery_status = fields.Char('Delivery Status', required=True)
	line_ids = fields.One2many('stock.picking.batch.has.return.line', 'wizard_id', string="Wizard")

	notes = fields.Char(string="Notes")

	def confirm(self):
		# if all qty received == 0 
		# will update delivery status to 'failed'
		not_received = self.line_ids.mapped(lambda r:r.qty_received==0)
		if all(not_received):
			self.delivery_status='failed'


		all_received = self.line_ids.mapped(lambda r:r.qty_received>0 and r.qty_received==r.move_line_id.qty_done)
		if all(all_received):
			raise ValidationError(_("Error!\nSemua barang DITERIMA!\nJika semua barang diterima maka klik tombol receive!"))

		self.picking_id.delivery_status = self.delivery_status
		lines = []

		for line in self.line_ids:
			lines.append((0,0,{'move_line_id': line.move_line_id.id, 'qty':line.qty, 'qty_received':line.qty_received}))
		data = {
			'batch_id':self.batch_id.id,
			'picking_id':self.picking_id.id,
			'delivery_status':self.delivery_status,
			'line_ids':lines
		}
		# self.create(data)
		return {'type': 'ir.actions.act_window_close'}

class StockPickingBatchHasReturnLine(models.TransientModel):
	_name = 'stock.picking.batch.has.return.line'
	_description = 'Stock Picking Batch Has Return Line'

	wizard_id = fields.Many2one('stock.picking.batch.has.return', string="Wizard", required=True, ondelete="cascade", onupdate='cascade')
	move_line_id = fields.Many2one('stock.move.line', string="Move Line", required=True, ondelete="cascade",onupdate="cascade")
	qty = fields.Float('Qty', related="move_line_id.qty_done", readonly=True)


	qty_received = fields.Float("Qty Received")


	# @api.onchange('move_line_id')
	# def onchange_move_line_id(self):
	# 	if self.move_line_id.id:
	# 		self.qty = self.move_line_id.qty_done


	@api.onchange('qty_received')
	def onchange_qty_received(self):
		if not self.move_line_id.id:
			raise ValidationError(_('Mohon isi produk terlebih dahulu!'))

		if self.qty_received>self.move_line_id.qty_done:
			raise ValidationError(_("Item Qty Received yang di kirim tidak boleh lebih besar dari yang dikirim (%s)." % (self.move_line_id.qty_done,)))

		if self.qty_received<0:
			self.qty_received=0


class PickupValidationWizard(models.TransientModel):
	_name = 'pickup.validation.wizard'
	_description = 'Pickup Validation Wizard'


	batch_id = fields.Many2one('stock.picking.batch', required=True, string="Batch/Memo", ondelete="cascade", onupdate="cascade")
	location_id = fields.Many2one('stock.location', string="Pickup Location")

	line_ids = fields.One2many('pickup.validation.line.wizard', 'wizard_id', string="Item(s)")


	@api.onchange('location_id')
	def onchange_location_id(self):
		if self.location_id:
			move_lines_in_location = self.batch_id.move_line_ids.filtered(lambda r:r.location_id.id==self.location_id.id and r.pickup_validated==False)
			lines = []
			if len(move_lines_in_location):
				for l in move_lines_in_location:
					lines.append((0,0,{'move_line_id':l.id, 'qty_done':l.qty_done}))

			self.line_ids = lines

	def _check_all_validated(self):
		no_validated = self.batch_id.move_line_ids.filtered(lambda r:r.pickup_validated==False)

		# if all validated
		if len(no_validated)==0:
			# self.batch_id.picking_ids.action_done()
			self.batch_id.write({'state':'checking'})

	def _check_is_all_qty_done_zero(self):
		for picking in self.line_ids.mapped(lambda r:r.move_line_id.picking_id):
			zero_done = picking.move_line_ids.mapped(lambda r:r.qty_done==0)
			if all(zero_done):
				picking.delivery_failed()

	def validate(self):
		self.ensure_one()
		for line in self.line_ids:
			line.move_line_id.write({'pickup_validated':True,'pickup_validated_by':self.env.user.id, 'qty_done':line.qty_done,'pickup_qty':line.qty_done})

		# self._check_is_all_qty_done_zero()
		# _logger.critical((line.qty_done,line.product_id.name))
		# raise ValidationError("PPPP")

		self._check_all_validated()


class PickupValidationLineWizard(models.TransientModel):
	_name = 'pickup.validation.line.wizard'
	_description = 'Pickup Validation Line Wizard'


	wizard_id = fields.Many2one('pickup.validation.wizard', required=True, string="Wizard", ondelete="cascade",onupdate="cascade")
	move_line_id = fields.Many2one('stock.move.line', required=True, string="Move Line", ondelete="cascade", onupdate='cascade')
	product_id = fields.Many2one('product.product', related="move_line_id.product_id", readonly=True)
	external_pickup_partner = fields.Many2one('res.partner', related="move_line_id.external_pickup_partner", readonly=True)
	product_uom_id = fields.Many2one('product.uom', related="move_line_id.product_uom_id", readonly=True)
	qty_done = fields.Float('Qty Done', required=True)


class StockPickingBatch(models.Model):
	_inherit = 'stock.picking.batch'

	send_time = fields.Datetime(string="Sending Time", required=False)
	# region_id = fields.Many2one('region',string="Delivery Region/Area", required=False)
	region_ids = fields.One2many('region', compute="_compute_region_ids", string="Regions")
	location_ids = fields.One2many('stock.location', string="Locations", compute="_compute_location_ids")
	location_ids_caption = fields.Char("Locations", compute="_compute_location_ids")
	move_lines = fields.One2many('stock.move', compute="_compute_stock_move", string="Moves")
	move_line_ids = fields.One2many('stock.move.line', compute="_compute_stock_move", string="Move Lines")

	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'Running'),
		('checking','Checking'),
		('finish','Finish'),
		('done', 'Done'),
		('cancel', 'Cancelled')], default='draft',
		copy=False, track_visibility='onchange', required=True)

	
	def _compute_location_ids(self):
		for rec in self:
			rec.location_ids = rec.move_line_ids.mapped(lambda r:r.location_id)
			rec.location_ids_caption = ",".join(rec.location_ids.mapped('name'))

	@api.depends('picking_ids.partner_id')
	def _compute_region_ids(self):
		for rec in self:
			regions = rec.picking_ids.mapped(lambda r:r.partner_id.region_city_id)
			rec.region_ids = regions

	@api.multi
	def _compute_stock_move(self):
		for rec in self:
			rec.move_lines = rec.picking_ids.mapped('move_lines')
			rec.move_line_ids = rec.picking_ids.mapped('move_line_ids')

	def set_draft(self):
		self.ensure_one()
		self.write({'state':'draft'})

	@api.multi
	def print_picking(self):
		pickings = self.mapped('picking_ids')
		if not pickings:
			raise UserError(_('Nothing to print.'))
		pickings.write({'printed':True})

		autodone = [
			'JNE', 'J&T', 'GRAB', 'grab', 'gojek', 
			'sicepat', 'beli2', 'Selfpickup', 'Lion Parcel', 'Ninja Express', 
			'BEST', 'Anteraja','LEX','IDEXPRESS','shopeeexpress',
			'JNE AGEN', 'JNE Lazada', 'LEX-Lazada'
		]
		if self.user_id.name in autodone:
			if self.state == 'draft':
				self.write({'state': 'done', 'send_time': fields.Datetime.now()})

				assigned_picking_lst = pickings.filtered(
					lambda m: m.state not in ('done', 'cancel'))
				assigned_picking_lst.write({'delivery_status': 'received'})

				assigned_move_line = assigned_picking_lst.mapped('move_line_ids').filtered(
					lambda m: m.state not in ('done', 'cancel'))
				for move_line in assigned_move_line:
					move_line.write(
						{'pickup_validated': True, 'pickup_validated_by': self.env.uid,
						 'pickup_qty': move_line.qty_done})

				quantities_done = sum(
					move_line.qty_done for move_line in assigned_move_line
				)
				if not quantities_done:
					return assigned_picking_lst.action_immediate_transfer_wizard()
				if assigned_picking_lst._check_backorder():
					return assigned_picking_lst.action_generate_backorder_wizard()
				assigned_picking_lst.action_done()
		else:
			if self.state=='draft':
				self.write({'state':'in_progress','send_time':fields.Datetime.now()})

		document = self.env.ref('base_glodok.action_report_picking_batch_memo').report_action(self)

		# _logger.critical(document)

		return document




	def send(self):
		self.write({'state':'send'})

	def finish(self):
		self.state='finish'

	@api.multi
	def cancel_picking(self):
		# self.mapped('picking_ids').action_cancel()
		# return self.write({'state': 'cancel'})
		return False



	def group_move_line_by_source_location(self):
		self.ensure_one()
		locations = self.move_line_ids.mapped(lambda r:r.location_id)
		res = []
		external_loc = self.env.ref('stock.warehouse0').external_loc
		for loc in locations.filtered(lambda r:r.id!=external_loc.id):
			move_lines = self.move_line_ids.filtered(lambda r:r.location_id.id==loc.id).sorted(lambda r:r.picking_id.origin)
			external = False
			line = {'location':loc, 'lines':move_lines, 'external':external, 'vendor':move_lines[0].external_pickup_partner}
			res.append(line)

		# external loc
		if external_loc.id in locations.ids:
			move_lines = self.move_line_ids.filtered(lambda r:r.location_id.id==external_loc.id).sorted(lambda r:r.picking_id.origin)
			suppliers = move_lines.mapped('external_pickup_partner')

			for supplier in suppliers:
				filtered_move_lines = move_lines.filtered(lambda r:r.external_pickup_partner.id==supplier.id)
				line = {'location':external_loc, 'lines':filtered_move_lines, 'external':True, 'vendor':filtered_move_lines[0].external_pickup_partner}
				res.append(line)
		return res



	def _open_pickup_validation_wizard(self):
		form = self.env.ref('base_glodok.pickup_validation_wizard_form')
		
		context = dict(self.env.context or {})
		if self.env.user.default_location_id.id!=False:
			context['default_location_id'] = self.env.user.default_location_id.id
		context['default_batch_id'] = self.id
		res = {
			'name': "%s" % (_('Pickup Validation')),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'pickup.validation.wizard',
			'view_id': form.id,
			'type': 'ir.actions.act_window',
			'context': context,
			'target': 'new',
		}
		return res
	def validate_wh(self):
		return self._open_pickup_validation_wizard()

	def force_done(self):
		self.write({'state':'done'})
	def force_finish(self):
		self.write({'state':'finish'})

	def force_in_progress(self):
		self.write({'state':'in_progress'})

	def check_no_status(self):
		no_status = self.picking_ids.filtered(lambda r:r.delivery_status==False or r.delivery_status=='')
		if len(no_status):
			raise ValidationError(_('Mohon Cek SJ: \n%s\nSurat Jalan tersebut belum didefinisikan status pengiriman nya!' % ("\n-".join(no_status.mapped('name')), )))
		return True

	def check_all_received(self):
		received = self.picking_ids.filtered(lambda r:r.delivery_status=='received')
		# find has_return wizard
		for r in received:
			find_wizard = self.env['stock.picking.batch.has.return'].search([('picking_id','=',r.id), ('batch_id','=',self.id)])
			if find_wizard:
				find_wizard.unlink()

		return True

	def check_has_return(self):
		has_return = self.picking_ids.filtered(lambda r:r.delivery_status=='has_return')
		# find has_return wizard
		for r in has_return:
			find_wizard = self.env['stock.picking.batch.has.return'].search([('picking_id','=',r.id), ('batch_id','=',self.id)])
			if not len(find_wizard):
				raise ValidationError(_('Mohon definisikan ulang Status Pengiriman SJ %s' % (r.name)))
		return True

	def check_failed(self):
		failed = self.picking_ids.filtered(lambda r:r.delivery_status=='failed')
		for r in failed:
			find_wizard = self.env['stock.picking.batch.has.return'].search([('picking_id','=',r.id), ('batch_id','=',self.id)])
			if not len(find_wizard):
				raise ValidationError(_('Mohon definisikan ulang Status Pengiriman SJ %s' % (r.name)))

		return True

	def action_picking_done(self, picking):
		self.ensure_one()
		picking.action_done()
		# raise ValidationError("PPP")
		if picking.state!='done':
			raise ValidationError(_("Gagal mengupdate status picking ke \"Done\". Ref-> %s - %s" % (self.name, picking.name,)))
	def create_sale_follow_up_schedule(self, picking, wizard):
		# write need follow up
		sale = picking.group_id.sale_id
		sale.write({'need_follow_up':1})

		# create remider to salesman
		new_sch_data = {
			'activity_type_id':self.env.ref('mail.mail_activity_data_call').id,
			'note':"SJ %s Gagal dikirim karena %s" % (picking.name, wizard.notes,),
			'res_model':'sale.order',
			'res_model_id':self.env.ref('sale.model_sale_order').id,
			'res_id':sale.id,
		}

		new_obj = self.env['mail.activity'].new(new_sch_data)
		new_obj._onchange_activity_type_id()
		new_data = new_obj._convert_to_write({name:new_obj[name] for name in new_obj._cache})
		new_data['user_id'] = sale.user_id.id
		new_data['date_deadline'] = fields.Date.today()
		new_sch = self.env['mail.activity'].create(new_data)


	def _create_incoming(self, stock_move_line):
		_logger.critical("CALL CREATE_INCOMING")
		picking = stock_move_line.picking_id
		not_reserved = stock_move_line
		new_data = {
			'picking_type_id':self.env.ref('stock.picking_type_in').id,
			'partner_id':not_reserved[0].external_pickup_partner.id,
			'origin':'PickedUP-%s-%s' % (self.name, picking.name)
		}
		return_location = self.env.ref('stock.warehouse0').default_return_location_id
		# if self.env.user.default_location_id.id:
		# 	return_location = self.env.user.default_location_id

		supplier_location = self.env.ref('stock.stock_location_suppliers')

		tmp_obj = self.env['stock.picking'].new(new_data)
		tmp_obj.onchange_picking_type()
		tmp_obj.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
		incoming_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
		incoming_data['origin'] = 'Sending Fail and PickedUP %s [%s]' % (self.name, picking.name)
		del incoming_data['move_lines']
		incoming = self.env['stock.picking'].create(incoming_data)
		move_lines = []
		for ll in not_reserved:
			# item incoming
			tmp_move_data = {
				'picking_id':incoming.id,
				'product_id':ll.product_id.id,
				# 'product_uom_qty':ll.pickup_qty, #incoming qty == picked up
				'product_uom_qty':ll.pickup_qty - ll.wizard_return_qty, #incoming qty == picked up
				'product_uom':ll.product_uom_id.id
			}
			
			tmp_move_data.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
			tmp_move = self.env['stock.move'].new(tmp_move_data)
			tmp_move.onchange_product_id()

			move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
			# move_lines.append((0,0,move_data))
			new_move = self.env['stock.move'].create(move_data)
			_logger.warning(("XXXX",new_move, new_move.name, new_move.product_qty, incoming.name))

		incoming.action_confirm()
		incoming.action_assign()

		# _logger.critical(incoming.button_validate())
		res_validation = incoming.button_validate()
		if res_validation!=None:
			# stock.immediate.transfer
			# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
			if res_validation.get('type')=='ir.actions.act_window':
				if res_validation.get('res_model',False) == 'stock.immediate.transfer':
					wiz_id = res_validation.get('res_id')
					wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
					# _logger.critical(">>>>>>>>>>>>>>>>")
					wiz.process()
				else:
					raise ValidationError("Else on iraction window return validate incoming!")

	def handle_external_pickup(self, picking):
		self.ensure_one()
		external_picked_up = picking.move_line_ids.filtered(lambda r:r.location_id.id==self.env.ref('stock.warehouse0').external_loc.id and r.pickup_qty>0)
		if len(external_picked_up)>0:
			
			not_reserved = external_picked_up.filtered(lambda r:r.product_uom_qty==0)
			_logger.critical(('NOT RESERVED PICKUP --->', not_reserved))
			if len(not_reserved):
				# make incoming if from reserved==0
				new_data = {
					'picking_type_id':self.env.ref('stock.picking_type_in').id,
					'partner_id':not_reserved[0].external_pickup_partner.id,
					'origin':'PickedUP-%s-%s' % (self.name, picking.name)
				}
				return_location = self.env.ref('stock.warehouse0').default_return_location_id
				# if self.env.user.default_location_id.id:
				# 	return_location = self.env.user.default_location_id

				supplier_location = self.env.ref('stock.stock_location_suppliers')

				tmp_obj = self.env['stock.picking'].new(new_data)
				tmp_obj.onchange_picking_type()
				tmp_obj.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
				incoming_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
				incoming_data['origin'] = 'Sending Fail and PickedUP from Supplier - %s [%s]' % (self.name, picking.name)
				del incoming_data['move_lines']
				incoming = self.env['stock.picking'].create(incoming_data)
				move_lines = []
				for ll in not_reserved:
					# item incoming
					tmp_move_data = {
						'picking_id':incoming.id,
						'product_id':ll.product_id.id,
						# 'product_uom_qty':ll.pickup_qty, #incoming qty == picked up
						'product_uom_qty':ll.pickup_qty - ll.wizard_return_qty, #incoming qty == picked up
						'product_uom':ll.product_uom_id.id
					}
					
					tmp_move_data.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
					tmp_move = self.env['stock.move'].new(tmp_move_data)
					tmp_move.onchange_product_id()

					move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
					# move_lines.append((0,0,move_data))
					new_move = self.env['stock.move'].create(move_data)
					_logger.warning(("PPPPP",new_move, new_move.name, new_move.product_qty))

				incoming.action_confirm()
				incoming.action_assign()

				# _logger.critical(incoming.button_validate())
				res_validation = incoming.button_validate()
				if res_validation!=None:
					# stock.immediate.transfer
					# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
					if res_validation.get('type')=='ir.actions.act_window':
						if res_validation.get('res_model',False) == 'stock.immediate.transfer':
							wiz_id = res_validation.get('res_id')
							wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
							# _logger.critical(">>>>>>>>>>>>>>>>")
							wiz.process()
						else:
							raise ValidationError("Else on iraction window return validate incoming!")

				_logger.info((incoming.name, incoming.state))

			# START pickedup but reserved
			# will create internal transfer
			reserved = external_picked_up.filtered(lambda r:r.product_uom_qty>0)
			_logger.info(('RESERVED PICKUP --->', reserved))
			if len(reserved):
				# make intenral_transfer if from reserved>0
				
				# make internal_transfer if from reserved==0
				new_data = {
					'picking_type_id':self.env.ref('stock.picking_type_internal').id,
					'partner_id':reserved[0].external_pickup_partner.id,
					'origin':'Send Failed %s [%s]' % (self.name, picking.name)
				}
				return_location = self.env.ref('stock.warehouse0').default_return_location_id
				# if self.env.user.default_location_id.id:
				# 	return_location = self.env.user.default_location_id

				

				tmp_obj = self.env['stock.picking'].new(new_data)
				tmp_obj.onchange_picking_type()
				location = reserved[0].location_id
				tmp_obj.update({'location_id':location.id, 'location_dest_id':return_location.id})
				internal_transfer_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
				internal_transfer_data['origin'] = 'Send Failed %s [%s]' % (self.name, picking.name)
				del internal_transfer_data['move_lines']
				internal_transfer = self.env['stock.picking'].create(internal_transfer_data)
				move_lines = []
				for ll in reserved:

					# item internal_transfer
					tmp_move_data = {
						'picking_id':internal_transfer.id,
						'product_id':ll.product_id.id,
						'product_uom_qty':ll.pickup_qty, #internal_transfer qty == picked up
						'product_uom':ll.product_uom_id.id
					}
					
					tmp_move_data.update({'location_id':location.id, 'location_dest_id':return_location.id})
					tmp_move = self.env['stock.move'].new(tmp_move_data)
					tmp_move.onchange_product_id()

					move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
					# move_lines.append((0,0,move_data))
					new_move = self.env['stock.move'].create(move_data)
					_logger.warning(("WWWW",new_move, new_move.name, new_move.product_qty))

				internal_transfer.action_confirm()
				internal_transfer.action_assign()
				# _logger.critical(internal_transfer.button_validate())

				res_validation = internal_transfer.button_validate()

				if res_validation!=None:
					# stock.immediate.transfer
					# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
					if res_validation.get('type')=='ir.actions.act_window':
						if res_validation.get('res_model',False) == 'stock.immediate.transfer':
							wiz_id = res_validation.get('res_id')
							wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
							# _logger.critical(">>>>>>>>>>>>>>>>")
							wiz.process()
						else:
							raise ValidationError("Else on iraction window return validate internal_transfer!")
				_logger.info((internal_transfer.name, internal_transfer.state, internal_transfer.move_line_ids.mapped(lambda r:"From:%s to %s" % (r.location_id.name,r.location_dest_id.name,))))
		# raise ValidationError('EEE')

	def create_internal_to_main_loc(self, move_line_ids):
		_logger.critical('Creating Internal To Main Loc')
		picking = move_line_ids[0].picking_id
		reserved = move_line_ids
		# make internal_transfer if from reserved==0
		new_data = {
			'picking_type_id':self.env.ref('stock.picking_type_internal').id,
			'origin':'Send Failed %s [%s]' % (self.name, picking.name)
		}
		return_location = self.env.ref('stock.warehouse0').default_return_location_id
		# if self.env.user.default_location_id.id:
		# 	return_location = self.env.user.default_location_id

		

		tmp_obj = self.env['stock.picking'].new(new_data)
		tmp_obj.onchange_picking_type()
		location = reserved[0].location_id
		tmp_obj.update({'location_id':location.id, 'location_dest_id':return_location.id})
		internal_transfer_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
		internal_transfer_data['origin'] = 'Send Failed %s [%s]' % (self.name, picking.name)
		del internal_transfer_data['move_lines']
		internal_transfer = self.env['stock.picking'].create(internal_transfer_data)
		move_lines = []
		_logger.critical(("KKKK", reserved))
		for ll in reserved:

			# item internal_transfer
			tmp_move_data = {
				'picking_id':internal_transfer.id,
				'product_id':ll.product_id.id,
				'product_uom_qty':ll.pickup_qty, #internal_transfer qty == picked up
				'product_uom':ll.product_uom_id.id
			}
			
			tmp_move_data.update({'location_id':location.id, 'location_dest_id':return_location.id})
			tmp_move = self.env['stock.move'].new(tmp_move_data)
			tmp_move.onchange_product_id()

			move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
			# move_lines.append((0,0,move_data))
			new_move = self.env['stock.move'].create(move_data)
			_logger.warning(("HHHHHH----HHHHHHH",new_move, new_move.name, new_move.product_qty, new_move.product_uom_qty))

		internal_transfer.action_confirm()
		internal_transfer.action_assign()
		# 
		# _logger.critical(internal_transfer.button_validate())
		_logger.critical(("Internal Assigned -->" , internal_transfer.state))
		if internal_transfer.state=='confirmed':
			# if no transfer
			# create stock move line manual
			for mv_line in internal_transfer.move_lines:
				mvl = self.env['stock.move.line']
				mvl.create({
					'move_id': mv_line.id,
					'product_id': mv_line.product_id.id,
					'product_uom_id': mv_line.product_uom.id,
					'location_id': internal_transfer.location_id.id,
					'location_dest_id': internal_transfer.location_dest_id.id,
					'picking_id': internal_transfer.id,
					'qty_done':mv_line.product_qty
					})
		# _logger.critical((internal_transfer.move_line_ids.mapped(lambda r:"%s - %s / %s (from %s to %s)" % (r.product_id.name, r.product_qty, r.qty_done, r.location_id.name, r.location_dest_id.name))))
		# raise ValidationError('EE')
		res_validation = internal_transfer.button_validate()
		if res_validation!=None:
			# stock.immediate.transfer
			# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
			if res_validation.get('type')=='ir.actions.act_window':
				if res_validation.get('res_model',False) == 'stock.immediate.transfer':
					wiz_id = res_validation.get('res_id')
					wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
					# _logger.critical(">>>>>>>>>>>>>>>>")
					wiz.process()
				else:
					raise ValidationError("Else on iraction window return validate internal_transfer!")
		_logger.info((internal_transfer.name, internal_transfer.state, internal_transfer.move_line_ids.mapped(lambda r:"From:%s to %s" % (r.location_id.name,r.location_dest_id.name,))))

	def create_report(self):
		self.ensure_one()
		external_loc = self.env.ref('stock.warehouse0').external_loc
		for picking in self.picking_ids:
			if picking.delivery_status=='has_return':
				wizard = self.env['stock.picking.batch.has.return'].search([('picking_id','=',picking.id), ('batch_id','=',self.id)], limit=1).sorted('id',reverse=True)
				if not len(wizard)>0:
					raise ValidationError("No Return Defined for Has Return")

				self.handle_external_pickup(picking)
				# update qty receive by has.return
				for line in wizard.line_ids:
					# update qty done is received qty
					line.move_line_id.write({'qty_done':line.qty_received})
					_logger.info(("qty done %s , received %s " % (line.move_line_id.pickup_qty, line.qty_received)))
					if line.move_line_id.location_id.id!=external_loc.id and line.move_line_id.pickup_qty>0:
						# just only for non external pickup
						# because external pickup has been validated on self.handle_external_pickup() , up this method
						if line.move_line_id.pickup_qty > line.qty_received:
							self._create_incoming(line.move_line_id)
				# validate picking then
				# create return
				# by wizard
				_logger.critical("Call Action Picking Done %s" % picking.name)
				self.action_picking_done(picking)
				picking.message_post(body="Reason: %s" % (wizard.notes,))

				self.create_sale_follow_up_schedule(picking,wizard)

			elif picking.delivery_status=='failed':
				wizard = self.env['stock.picking.batch.has.return'].search([('picking_id','=',picking.id), ('batch_id','=',self.id)], limit=1).sorted('id',reverse=True)
				if not len(wizard)>0:
					raise ValidationError("No Return Defined for Failed")
				# if all failed
				# check if there take from via external resource
				# if any external resource who already picked up will create incoming to paris
				external_picked_up = picking.move_line_ids.filtered(lambda r:r.location_id.id==self.env.ref('stock.warehouse0').external_loc.id and r.pickup_qty>0)
				if len(external_picked_up)>0:
					
					not_reserved = external_picked_up.filtered(lambda r:r.product_uom_qty==0)
					if len(not_reserved):
						# make incoming if from reserved==0
						new_data = {
							'picking_type_id':self.env.ref('stock.picking_type_in').id,
							'partner_id':not_reserved[0].external_pickup_partner.id,
							'origin':'PickedUP-%s-%s' % (self.name, picking.name)
						}
						return_location = self.env.ref('stock.warehouse0').default_return_location_id
						# if self.env.user.default_location_id.id:
						# 	return_location = self.env.user.default_location_id

						supplier_location = self.env.ref('stock.stock_location_suppliers')

						tmp_obj = self.env['stock.picking'].new(new_data)
						tmp_obj.onchange_picking_type()
						tmp_obj.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
						incoming_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
						incoming_data['origin'] = 'Send Fail and PickedUP from Supplier - %s [%s]' % (self.name, picking.name)
						del incoming_data['move_lines']
						incoming = self.env['stock.picking'].create(incoming_data)
						move_lines = []
						for ll in not_reserved:
							# item incoming
							tmp_move_data = {
								'picking_id':incoming.id,
								'product_id':ll.product_id.id,
								'product_uom_qty':ll.pickup_qty, #incoming qty == picked up
								'product_uom':ll.product_uom_id.id
							}
							
							tmp_move_data.update({'location_id':supplier_location.id, 'location_dest_id':return_location.id})
							tmp_move = self.env['stock.move'].new(tmp_move_data)
							tmp_move.onchange_product_id()

							move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
							# move_lines.append((0,0,move_data))
							new_move = self.env['stock.move'].create(move_data)
							_logger.warning((new_move, new_move.name, new_move.product_qty))

						incoming.action_confirm()
						incoming.action_assign()
						# _logger.critical(incoming.button_validate())
						res_validation = incoming.button_validate()
						if res_validation!=None:
							# stock.immediate.transfer
							# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
							if res_validation.get('type')=='ir.actions.act_window':
								if res_validation.get('res_model',False) == 'stock.immediate.transfer':
									wiz_id = res_validation.get('res_id')
									wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
									# _logger.critical(">>>>>>>>>>>>>>>>")
									wiz.process()
								else:
									raise ValidationError("Else on iraction window return validate incoming!")

						_logger.critical(('====>',incoming.state, incoming.move_line_ids.mapped(lambda r:"%s -> %s(%s)" % (r.product_id.name, r.product_uom_qty, r.qty_done))))

					# START pickedup but reserved
					# will create internal transfer
					reserved = external_picked_up.filtered(lambda r:r.product_uom_qty>0)
					if len(reserved):
						# make intenral_transfer if from reserved>0
						
						# make internal_transfer if from reserved==0
						new_data = {
							'picking_type_id':self.env.ref('stock.picking_type_internal').id,
							'partner_id':reserved[0].external_pickup_partner.id,
							'origin':'Send Failed %s [%s]' % (self.name, picking.name)
						}
						return_location = self.env.ref('stock.warehouse0').default_return_location_id
						# if self.env.user.default_location_id.id:
						# 	return_location = self.env.user.default_location_id

						

						tmp_obj = self.env['stock.picking'].new(new_data)
						tmp_obj.onchange_picking_type()
						location = reserved[0].location_id
						tmp_obj.update({'location_id':location.id, 'location_dest_id':return_location.id})
						internal_transfer_data = tmp_obj._convert_to_write({name:tmp_obj[name] for name in tmp_obj._cache})
						internal_transfer_data['origin'] = 'Send Failed %s [%s]' % (self.name, picking.name)
						del internal_transfer_data['move_lines']
						internal_transfer = self.env['stock.picking'].create(internal_transfer_data)
						move_lines = []
						for ll in reserved:

							# item internal_transfer
							tmp_move_data = {
								'picking_id':internal_transfer.id,
								'product_id':ll.product_id.id,
								'product_uom_qty':ll.pickup_qty, #internal_transfer qty == picked up
								'product_uom':ll.product_uom_id.id
							}
							
							tmp_move_data.update({'location_id':location.id, 'location_dest_id':return_location.id})
							tmp_move = self.env['stock.move'].new(tmp_move_data)
							tmp_move.onchange_product_id()

							move_data = tmp_move._convert_to_write({name:tmp_move[name] for name in tmp_move._cache})
							# move_lines.append((0,0,move_data))
							new_move = self.env['stock.move'].create(move_data)
							_logger.warning((new_move, new_move.name, new_move.product_qty))

						internal_transfer.action_confirm()
						internal_transfer.action_assign()
						# _logger.critical(internal_transfer.button_validate())
						res_validation = internal_transfer.button_validate()
						if res_validation!=None:
							# stock.immediate.transfer
							# _logger.critical((">>>>>>>>>>>>>>>>",res_validation))
							if res_validation.get('type')=='ir.actions.act_window':
								if res_validation.get('res_model',False) == 'stock.immediate.transfer':
									wiz_id = res_validation.get('res_id')
									wiz = self.env['stock.immediate.transfer'].search([('id','=',wiz_id)])
									# _logger.critical(">>>>>>>>>>>>>>>>")
									wiz.process()
								else:
									raise ValidationError("Else on iraction window return validate internal_transfer!")
				from_stock = picking.move_line_ids.filtered(lambda r:r.location_id.id!=self.env.ref('stock.warehouse0').external_loc.id and r.pickup_qty>0)
				
				_logger.critical(("FROM STOCK", from_stock))
				if from_stock:

					self.create_internal_to_main_loc(from_stock)

				picking.with_context({'batch_action':1}).action_cancel()
				picking.message_post(body="Reason: %s" % (wizard.notes,))

				self.create_sale_follow_up_schedule(picking, wizard)
			else:
				# if received
				self.action_picking_done(picking)
			_logger.critical(("%s(%s) --> %s" % (picking.name, picking.delivery_status, picking.state)))
			_logger.critical(picking.move_line_ids.mapped(lambda r:"%s - %s --> %s" % (r.product_id.display_name, r.ordered_qty, r.qty_done)))
		# update batch picking state
		self.write({'state':'done'})

	def check_picking_status(self):
		self.ensure_one()
		cancel = self.picking_ids.filtered(lambda r:r.state=='cancel')
		if len(cancel):
			raise ValidationError("Ada Surat Jalan yang berstatus \"CANCEL\". Mohon Di Cek:\n%s" % (",".join(cancel.mapped('name'))))


	def post(self):
		self.check_picking_status()
		self.check_no_status()
		self.check_all_received()
		self.check_has_return()
		self.check_failed()
		self.create_report()

		# raise ValidationError("EEE")
