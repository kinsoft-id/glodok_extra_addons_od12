# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,tools
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProductSalesQtyReport(models.Model):
	_name = 'product.sales.qty.report'
	_description = 'Product Sales Qty Report'

	_auto = False

	product_id = fields.Many2one('product.product', string="Product", readonly=True)
	product_tmpl_id = fields.Many2one('product.template', string="Product Templat", readonly=True)
	product_uom_qty = fields.Float('Qty', readonly=True, group_operator='sum')
	date_series = fields.Date(string="Date Series", readonly=True)

	uom_id = fields.Many2one('product.uom', string="UOM", related="product_tmpl_id.uom_id", readonly=True)

	
	def _select(self):
		query = """
			WITH series AS (
				SELECT date_trunc('day', dd)::date as ds
				FROM generate_series(
						(
							SELECT NOW()-(CONCAT(icp.value,' day')::interval)
							FROM ir_config_parameter  icp
							-- WHERE key='auth_signup.template_user_id'
							WHERE key='interval.product_sales_qty_report'
						)
						, now()::timestamp
						, '1 day'::interval
				) dd
			)
			SELECT 
				CONCAT(to_char(series.ds, 'YYYYMMDD'), LPAD(prod.product_tmpl_id::text,4,'0'))::bigint AS id
				,prod.id as product_id
				,prod.product_tmpl_id
				,SUM(CASE WHEN ps.product_id is NOT NULL THEN ps.product_uom_qty ELSE 0 END) AS product_uom_qty
				,series.ds as date_series
			FROM series 
			CROSS JOIN product_product prod
			LEFT JOIN (
				SELECT
					pp.id as product_id
					,pp.product_tmpl_id
					,(CASE WHEN sol.id IS NOT NULL THEN sol.product_uom_qty ELSE 0 END) AS product_uom_qty
					,so.date_order
					,so.id as so_id
				FROM product_product AS pp
				LEFT JOIN sale_order_line AS sol ON sol.product_id = pp.id AND sol.state='done'
				LEFT JOIN sale_order AS so ON so.id = sol.order_id
			) ps ON prod.id=ps.product_id and series.ds::date = ps.date_order::date
			GROUP BY prod.id,series.ds
		"""
		return query
	
	
	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			)""" % (self._table, self._select()))