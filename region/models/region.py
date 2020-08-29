# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class Region(models.Model):
	_name = 'region'
	_description = "Region"


	def _default_country_id(self):
		return self.env.ref('base.id').id

	code = fields.Char(string="Code", size=13, required=True, unique=True)
	name = fields.Char(string="Name", required=True)
	country_id = fields.Many2one('res.country', required=True, default=_default_country_id)
	parent_id = fields.Many2one('region', readonly=True, compute="_compute_parent", store=True)
	index_level = fields.Integer(string="Level No.", compute="_compute_parent", store=True)

	_selection_area_level = [('state/province','State/Province'), ('city','City'), ('district','District'), ('village','village')]

	area_level = fields.Selection(_selection_area_level, compute="_compute_parent", store=True)
	child_ids = fields.One2many('region', 'parent_id', string="Childs")

	# res_country_state_id = fields.Many2one('res.country.state', string="Odoo Res Country State")


	@api.depends('code')
	def _compute_parent(self):
		for rec in self:
			code = rec.code
			splitted_code = code.split(".")
			length_splitted = len(splitted_code)
			if length_splitted==1:
				parent_id = False
			else:
				parents = []
				for x in range(0,(length_splitted-1)):
					parents.append(splitted_code[x])
				parent_codes = ".".join(parents)
				parent = self.search([('code','=',parent_codes)])
				parent_id = parent.id

			index = (length_splitted-1)
			rec.update({
				'parent_id':parent_id,
				'index_level':index,
				'area_level':self._selection_area_level[index][0]
				})

	def remove_all_res_country_state_indonesia(self):
		_logger.info('Unlink All Country State (odoo data) For Indonesia')
		states = self.env['res.country.state'].search([('country_id','=',self.env.ref('base.id').id)])
		# unlink only who not has administrative area
		to_unlink = states.filtered(lambda r:len(r.region_ids)==0)
		_logger.info('Unlinking %s' % len(to_unlink))
		to_unlink.unlink()
		_logger.info("Unlink Finished!")

	def check_states(self):
		self.remove_all_res_country_state_indonesia()
		_logger.info('Starting Checking States!')
		states = self.filtered(lambda r:r.area_level=='state/province')
		_logger.info('Checking %s states' % len(states))
		not_found = self.env['region']
		indonesia =  self.env.ref('base.id')

		def create_res_country_state(indonesia, state):
			new_state_data = {
				'country_id':indonesia.id,
				'name':state.name,
				'code':state.code,
			}
			res_state = self.env['res.country.state'].create(new_state_data)

			return res_state
		for state in states:
			_logger.info('checking %s' % state.name)
			# find in res.country.state
			res_state = self.env['res.country.state'].search([('code','=',state.code)])

			if len(res_state)==0:
				not_found|=state
				_logger.info('State %s not found in res.country.state' % state.name)
				res_state = create_res_country_state(indonesia, state)
				state.res_country_state_id = res_state.id
			else:
				_logger.warning('Found %s: %s' % (res_state, ','.join(res_state.mapped('name'))))
				if len(res_state)==1:
					if res_state.country_id.id!=indonesia.id:
						res_state.unlink()
						res_state = create_res_country_state(indonesia, state)
				else:
					if len(res_state)>1:
						has_indo = res_state.filtered(lambda r:r.country_id.id==indonesia.id)
						if len(has_indo)>0:
							to_unlink = res_state.filtered(lambda r:r.country_id.id!=indonesia.id)
							to_unlink.unlink()
						elif len(has_indo)==0:
							res_state.unlink() #remove state wich same code in other countries
							# create new one for indonesia
							create_res_country_state(indonesia, state)