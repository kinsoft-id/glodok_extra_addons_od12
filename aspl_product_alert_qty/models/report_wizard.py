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

from odoo import models,fields,api
from datetime import datetime,date


class wizard_product(models.TransientModel):
    _name='wizard.report'

    group_by=fields.Selection(string="Group By",selection=[("category", "All Product"), ("location", "Location")], default='category')
    category_ids = fields.Many2many('product.category',string='Product Category')
    location_ids = fields.Many2many('stock.location', string='Product Location',domain=[('usage','=','internal')])


    breakdown_location = fields.Boolean(string="Breakdown Location", help="IF this checked on group by All Product will break down then quantity on each location")


    @api.onchange('group_by')
    def onchange_group_by(self):
        # always be false if filled
        self.breakdown_location = False

    @api.multi
    def action_print_report(self):
        datas={'form':self.read()[0], # it reads all data from wizard page
               'ids':self.id,
               'model':'wizard.report'
               }
        return self.env.ref('aspl_product_alert_qty.action_report_alert_qty_wizard').report_action(self,data=datas)

    @api.model
    def cron_btn_send_mail(self,group_by='category',breakdown_location=False,locations=None):
        if locations==None:
            locations = self.env['stock.location']

        template_id = self.env.ref('aspl_product_alert_qty.mail_template_alert_qty')
        wiz_id = self.env['wizard.report'].create({'group_by':group_by, 'breakdown_location':breakdown_location, 'location_ids':locations.ids})
        
        config_id = self.env['res.config.settings'].search([], limit=1, order="id desc")
        if config_id:
            for each in config_id.alert_user_ids:
                email = each.partner_id.email
                partner_name = each.partner_id.name
                result = template_id.with_context(email_to=email,name=partner_name,wizard_id=wiz_id.id).send_mail(wiz_id.id, force_send=True)
        else:
            raise ValidationError(_("Warning! \nPlease configure the settings first in Settings > Inventory."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: