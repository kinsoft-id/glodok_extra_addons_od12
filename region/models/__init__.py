from . import region

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, SUPERUSER_ID


def remove_all_indonesia_country_state(cr, registry):
	#write the default debit account on salary rule having xml_id like 'l10n_be_hr_payroll.1' up to 'l10n_be_hr_payroll.1409'
	env = api.Environment(cr, SUPERUSER_ID, {})
	data = env['res.country.state'].search([('country_id','=',env.ref('base.id').id)])
	data.unlink()

# def _register_region_to_res_country_state(cr, registry):
# 	env = api.Environment(cr, SUPERUSER_ID, {})
# 	data = env['region'].search([('country_id','!=',False)])