# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	default_code = fields.Char(
		'Internal Reference', compute='_compute_default_code',
		inverse='_set_default_code', store=True, track_visibility='onchange')
	
	@api.one
	def _set_default_code(self):
		if len(self.product_variant_ids) == 1:
			self.product_variant_ids.default_code = self.default_code

	@api.depends('product_variant_ids', 'product_variant_ids.default_code')
	def _compute_default_code(self):
		unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
		for template in unique_variants:
			template.default_code = template.product_variant_ids.default_code
		for template in (self - unique_variants):
			template.default_code = ''
	def dummy(self):
		return True