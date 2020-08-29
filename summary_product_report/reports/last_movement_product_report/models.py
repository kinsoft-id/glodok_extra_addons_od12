# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


class LastMovementProductReport(models.Model):
	_name = 'last.movement.product.report'
	_description = 'Last Movement Product Report'


	# uncomment if using tracking modules
	# _inherit = ['mail.thread', 'mail.activity.mixin']

	_auto = False

	product_id = fields.Many2one('product.product', string="Product", readonly=True)
	last_purchase_id = fields.Many2one('purchase.order', string="Last Purchase", readonly=True,compute="_compute_last")
	last_sale_id = fields.Many2one('sale.order', string="Last Sale", readonly=True,compute="_compute_last")
	days_diff_po = fields.Integer("Days Diff PO", readonly=True)
	days_diff_so = fields.Integer("Days Diff SO", readonly=True)
	active = fields.Boolean("Active", readonly=True)


	product_tmpl_id = fields.Many2one('product.template', string="Product Templat", readonly=True)

	immediately_usable_qty = fields.Float(related="product_id.immediately_usable_qty")
	uom_id = fields.Many2one(related="product_id.uom_id")
	availability = fields.Html(string="Availability", compute="_compute_availability")


	def _item_availability(self, locs):
		self.ensure_one()
		statuses = []
		Quant = self.env['stock.quant']
		for loc in locs:
			product_context = self.with_context(location=loc.id).product_id
			# _logger.critical((self.product_id.name,product_context.qty_available, product_context.outgoing_qty, product_context.immediately_usable_qty))
			
			prodquant = Quant.search([('location_id','=',loc.id), ('product_id','=',product_context.id)])
			# _logger.warning(prodquant.mapped('reserved_quantity'))
			reserved = sum(prodquant.mapped('reserved_quantity'))
			stock = product_context.immediately_usable_qty - reserved
			if stock>0:
				statuses.append("%s = %s" % (loc.display_name, stock))
		return "<br/>".join(statuses)


	def _compute_availability(self):
		locs = self.env['stock.location'].search([('usage','=','internal'),('scrap_location','=',False)])
		for rec in self:
			item_availability = rec._item_availability(locs)
			rec.availability = item_availability


	# so_line_ids = fields.One2many('sale.order.line', 'product_id', string="Sale Item", domain=[('state','in',['done'])], readonly=True)


	def _compute_last(self):
		for rec in self:
			self.update({
				'last_sale_id':False,
				'last_purchase_id':False
				})
	
	def _select(self):
		query = """
			WITH so AS (
				select 
					sol.id
					,sol.order_id
					,so.state
					,so.date_order
					,sol.product_id
					,DATE_PART('day', now() - so.date_order) as days_diff
				FROM sale_order_line sol
				JOIN sale_order so on so.id = sol.order_id
				WHERE so.state in ('done')
			), po AS (
				select
					po.id
					,po.date_order
					,pol.product_id
					,DATE_PART('day', now() - po.date_order) as days_diff
				FROM purchase_order_line AS pol
				JOIN purchase_order AS po ON po.id = pol.order_id
				WHERE po.state in ('done')
			)

			SELECT 
				p2.id
				,p2.product_id
				,p2.active
				,p2.product_tmpl_id
				,(CASE WHEN p2.days_diff_so IS NULL THEN 0 ELSE p2.days_diff_so END) AS days_diff_so
				,(CASE WHEN p2.days_diff_po IS NULL THEN 0 ELSE p2.days_diff_po END) AS days_diff_po
			FROM (
				SELECT 
					pp.id
					,pp.id AS product_id	
					,pp.product_tmpl_id as product_tmpl_id
					,pp.active
					,MIN(so.days_diff) as days_diff_so
					,MIN(po.days_diff) as days_diff_po
				FROM product_product AS pp
				LEFT JOIN  so ON so.product_id = pp.id
				LEFT JOIN po ON po.product_id = pp.id
				GROUP BY
					pp.id
					,pp.product_tmpl_id
					,pp.active
			) AS p2
		"""
		return query
	
	
	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			)""" % (self._table, self._select()))

	