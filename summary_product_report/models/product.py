# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
	_inherit = 'product.product'

	last_movement_report_ids = fields.One2many('last.movement.product.report', 'product_id', string="Last Movement Reports")
	qty_external = fields.Float(
		'Quantity On Hand', compute='_compute_quantities_ext', search='_search_qty_available',
		digits=dp.get_precision('Product Unit of Measure'))


	@api.depends('qty_external')
	def _compute_quantities_ext(self):
		for rec in self:
			rec.qty_external = rec.with_context(location=22).virtual_available


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	# uncomment if using tracking modules
	#_inherit = ['mail.thread', 'mail.activity.mixin']
	last_movement_report_ids = fields.One2many('last.movement.product.report', 'product_tmpl_id', string="Last Movement Reports")
	last_movement_report_id = fields.Many2one('last.movement.product.report', string="Last Movement Report", compute="_compute_last")
	last_days_diff_so  = fields.Integer(string="Days Diff Last Sale", compute="_compute_last")

	qty_external = fields.Float(
		'Quantity On Hand', compute='_compute_quantities_ext', search='_search_qty_available',
		digits=dp.get_precision('Product Unit of Measure'))

	def _search_qty_available(self, operator, value):
		if self._context.get('negative_available'):
			locations = self.env['stock.location'].search([('id','!=',22), ('usage','=','internal'), ('scrap_location','=',False)])
			res_ext = super(ProductTemplate, self.with_context(location=22))._search_qty_available('<', 0.0)
			product_ids_ext = res_ext[0][2]
			
			res_int = super(ProductTemplate, self.with_context(location=locations.ids))._search_qty_available('>', 0.0)
			product_ids_int = res_int[0][2]

			ids = [] 
			for prod_id in product_ids_int:
				if prod_id in product_ids_ext:
					ids.append(prod_id)
			return [('id','in',ids)]
		else:
			return super(ProductTemplate, self)._search_qty_available(operator, value)


	@api.depends('product_variant_ids.qty_external')
	def _compute_quantities_ext(self):
		for rec in self:
			if len(rec.product_variant_ids):
				rec.qty_external = rec.product_variant_ids[0].qty_external

	def _compute_last(self):
		for rec in self:
			if len(rec.last_movement_report_ids):
				last_movement_report_id = rec.last_movement_report_ids[0]
				diff = 0
				if last_movement_report_id.id:
					diff = last_movement_report_id.days_diff_so

				rec.update({
					'last_movement_report_id':last_movement_report_id,
					'last_days_diff_so':diff
				})
