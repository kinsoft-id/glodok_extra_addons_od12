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
	last_purchase_id = fields.Many2one('purchase.order', string="Last Purchase", readonly=True)
	last_sale_id = fields.Many2one('sale.order', string="Last Sale", readonly=True)
	days_diff_po = fields.Integer("Days Diff PO", readonly=True)
	days_diff_so = fields.Integer("Days Diff SO", readonly=True)
	active = fields.Boolean("Active", readonly=True)
	
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
				,p2.last_purchase_id
				,p2.last_sale_id
				,(CASE WHEN p2.days_diff_po IS NULL THEN 0 ELSE p2.days_diff_po END) AS days_diff_po
				,(CASE WHEN p2.days_diff_so IS NULL THEN 0 ELSE p2.days_diff_so END) AS days_diff_so
				,p2.active
			FROM (
				SELECT 
					pp.id
					,pp.id AS product_id
					,(select id FROM po WHERE po.product_id = pp.id ORDER BY po.date_order DESC LIMIT 1) AS last_purchase_id
					,(select id FROM so WHERE so.product_id = pp.id ORDER BY so.date_order DESC LIMIT 1) AS last_sale_id
					,(select days_diff FROM po WHERE po.product_id = pp.id ORDER BY po.date_order DESC LIMIT 1) AS days_diff_po
					,(select days_diff FROM so WHERE so.product_id = pp.id ORDER BY so.date_order DESC LIMIT 1) AS days_diff_so
					,pp.active
				FROM product_product AS pp
			) AS p2
		"""
		return query
	
	
	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			)""" % (self._table, self._select()))

	