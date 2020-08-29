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
from odoo.exceptions import ValidationError


class ProductQtyAlert(models.Model):
    _name = "product.qty.alert"

    product_id = fields.Many2one('product.product')
    location_id = fields.Many2one('stock.location',domain=[('usage','=','internal')])
    alert_qty = fields.Float(string="Alert Quantity")


class InheritmailTemplate(models.Model):
    _inherit = "mail.template"

    use_for_alert_qty = fields.Boolean(string="Use For Quantity Alert")




class InheritProduct(models.Model):
    _inherit = "product.product"

    alert_product_ids = fields.One2many('product.qty.alert','product_id', string="Alerts")
    same_for_all = fields.Boolean(string="Apply All", default=True)
    alert_qty = fields.Float(string="Alert Quantity")

    @api.multi
    def btn_print_report(self):
        datas = {'form': self.read()[0],
                 'ids': self.id,
                 'model': 'product.product'}
        return self.env.ref('aspl_product_alert_qty.action_report_alert_qty').report_action(self, data=datas)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # alert_product_ids = fields.One2many('product.qty.alert','product_id', string="Alerts")
    same_for_all = fields.Boolean(string="Apply All", default=True)
    alert_qty = fields.Float(string="Alert Quantity")
    show_in_alert = fields.Boolean(default=False, string="Show In Alert Stock Report")

    @api.constrains('same_for_all','alert_qty')
    def constrains_alert_products(self):
        for rec in self:
            rec.product_variant_ids.write({
                'same_for_all':rec.same_for_all,
                'alert_qty':rec.alert_qty
                })