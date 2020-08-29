# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProductSaleDailyAverage(models.Model):
	_name = 'product.sale.daily.average'
	_description = 'Product Sale Daily Average'


	# uncomment if using tracking modules
	#_inherit = ['mail.thread', 'mail.activity.mixin']

	_auto = False

	product_id = fields.Many2one('product.product', string="Product", readonly=True)
	daily_avg_qty = fields.Float('Daily Average Qty', readonly=True, group_operator='avg')
	uom_id = fields.Many2one('product.uom', string="UOM", readonly=True)
	
	def _select(self):
		query = """
			SELECT
				r.product_id as id
				,r.product_id
				,pt.uom_id
				,AVG(r.product_uom_qty) AS daily_avg_qty
			FROM product_sales_qty_report AS r
			LEFT JOIN product_template AS pt ON pt.id = r.product_tmpl_id
			GROUP BY r.product_id, pt.uom_id
		"""
		return query


	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			
			)""" % (self._table, self._select()))	

	