# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
	_inherit = 'res.users'
	default_location_id = fields.Many2one('stock.location', string="Default Location")

class ResPartner(models.Model):
	_inherit = 'res.partner'
	region_city_id = fields.Many2one('region',string="Region City", domain=[('area_level','=','city')])
	region_district_id = fields.Many2one('region',string="Region District", domain=[('area_level','=','district')])


	@api.onchange('region_city_id')
	def _onchange_region_city_id(self):
		self.region_district_id = False