# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval
import ast


class ProductAlertConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alert_user_ids = fields.Many2many('res.users',string="Alert User")
    alert_email_id = fields.Many2one('mail.template',string="Select Email Template")

    @api.model
    def get_values(self):
        res = super(ProductAlertConfigSettings, self).get_values()
        config_param_obj = self.env['ir.config_parameter']
        alert_user_ids = config_param_obj.sudo().get_param('alert_user_ids')
        if alert_user_ids:
            res.update({'alert_user_ids':ast.literal_eval(alert_user_ids)})
        res.update({
            'alert_email_id': int(config_param_obj.sudo().get_param('alert_email_id')),
        })
        return res

    @api.multi
    def set_values(self):
        super(ProductAlertConfigSettings, self).set_values()
        config_param_obj = self.env['ir.config_parameter'].sudo()
        config_param_obj.set_param("alert_user_ids", self.alert_user_ids.ids)
        config_param_obj.set_param("alert_email_id", self.alert_email_id.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: