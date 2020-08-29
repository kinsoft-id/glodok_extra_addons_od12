# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare

import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	@api.onchange('product_uom_qty', 'product_uom', 'route_id')
	def _onchange_product_id_check_availability(self):
		if not self.product_id or not self.product_uom_qty or not self.product_uom:
			self.product_packaging = False
			return {}
		if self.product_id.type == 'product':
			precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			product = self.product_id.with_context(
				warehouse=self.order_id.warehouse_id.id,
				lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
			)
			product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
			if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
				is_available = self._check_routing()
				if not is_available:
					detail_stock_on_locations_map = []

					locations = self.env['stock.location'].search([('id','!=',False),('active','=',True), ('usage','=','internal'),('scrap_location','=',False)])

					can_fill = []
					title = _('Not enough inventory!')
					for loc in locations:
						loc_stock = self.product_id.with_context(location=loc.id)
						detail_stock_on_locations_map.append("@ %s = %s" % (loc.name, loc_stock.virtual_available))
						can_fill.append(loc_stock.virtual_available>=product_qty)

					if any(can_fill):
						title = _('Maybe Not enough inventory!Please Check!')
					detail_stock_on_locations = "\n".join(detail_stock_on_locations_map)
					message =  _('You plan to sell %s %s but you only have %s %s available in %s warehouse. %s') % \
							(self.product_uom_qty, self.product_uom.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name, detail_stock_on_locations)
					# We check if some products are available in other warehouses.
					if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
						message += _('\nThere are %s %s available accross all warehouses.') % \
								(self.product_id.virtual_available, product.uom_id.name)


					warning_mess = {
						'title': title,
						'message' : message
					}
					return {'warning': warning_mess}
		return {}