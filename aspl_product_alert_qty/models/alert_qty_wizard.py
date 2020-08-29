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

from odoo import models, fields, api,_
from datetime import datetime, date
from odoo.exceptions import ValidationError, Warning


class AlertQtyWizard(models.TransientModel):
    _name = "alert.qty.wizard"

    apply_on = fields.Selection(string="Apply On",
                                selection=[('all', 'All'), ('product', 'Product'), ('category', 'Category')],
                                default='all')
    overwrite_exist_product = fields.Boolean(string="Overwrite Existing Products")
    product_ids = fields.Many2many('product.product', string="Products", domain=[('type', '=', 'product')])
    category_ids = fields.Many2many('product.category', string="Category")
    all_product_alert_ids = fields.One2many('location.qty', 'wizard_id')

    @api.multi
    def action_apply_to_products(self):
        list_id = []
        if self.apply_on == 'all':
            product_record = self.env['product.product'].search([('type', '=', 'product')])
            self.location_qty_add(product_record,list_id)

        elif self.apply_on == 'product':
            product_record = self.env['product.product'].search([('id', 'in', self.product_ids.ids)])
            self.location_qty_add(product_record,list_id)

        else:
            product_record = self.env['product.product'].search([('categ_id', 'in', self.category_ids.ids),('type', '=', 'product')])
            self.location_qty_add(product_record,list_id)

        view_id_tree = self.env.ref('product.product_product_tree_view').id
        view_id_form = self.env.ref('product.product_normal_form_view').id
        return {
            'name': 'Product Variants',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id_tree, 'tree'),(view_id_form, 'form')],
            'view_id': False,
            'domain': [('id', 'in', list_id)]
        }

    @api.multi
    def location_qty_add(self,product_record,list_id):
        for line in product_record:
            list = []
            for each in self.all_product_alert_ids:
                dict1 = {
                    'id': self.id,
                    'location_id': each.location_id.id,
                    'alert_qty': each.alert_qty,
                }
                if self.overwrite_exist_product == False:
                    count = 0
                    for ket in line.alert_product_ids:
                        if (each.location_id.id == ket.location_id.id):
                            count += 1
                            break
                    if count == 0:
                        list.append((0, 0, dict1))
                    list_id.append(line.id)
                else:
                    count = 0
                    for ket in line.alert_product_ids:
                        if (each.location_id.id == ket.location_id.id):
                            ket.alert_qty = each.alert_qty
                            count += 1
                            break
                    if count == 0:
                        list.append((0, 0, dict1))
                    list_id.append(line.id)
            line.alert_product_ids = list


class LocationQty(models.TransientModel):
    _name = "location.qty"

    wizard_id = fields.Many2one('alert.qty.wizard')
    location_id = fields.Many2one('stock.location', domain=[('usage', '=', 'internal')])
    alert_qty = fields.Float(string="Alert Quantity")

    @api.constrains('alert_qty')
    def _check_something(self):
        if self.alert_qty == 0 or self.alert_qty < 0:
            raise ValidationError(_("Products's alert qty should be greater then zero."))

        if self.wizard_id.apply_on == 'all':
            product_record = self.env['product.product'].search([('type', '=', 'product')])
            for rec in product_record:
                if self.alert_qty < rec.reordering_min_qty and self.alert_qty != 0:
                    raise ValidationError(_("%s alert qty should be greater then products's minimum qty %f."%(rec.name,rec.reordering_min_qty)))

        elif self.wizard_id.apply_on == 'category':
            product_record = self.env['product.product'].search([('categ_id', 'in', self.wizard_id.category_ids.ids), ('type', '=', 'product')])
            for rec in product_record:
                if self.alert_qty < rec.reordering_min_qty and self.alert_qty != 0:
                    raise ValidationError(_(" %s alert qty should be greater then products's minimum qty %f." %(rec.name,rec.reordering_min_qty)))
        else:
            for rec in self.wizard_id.product_ids:
                if self.alert_qty < rec.reordering_min_qty and self.alert_qty != 0:
                    raise ValidationError(_("%s alert qty should be greater then products's minimum qty %f."%(rec.name,rec.reordering_min_qty)))
                
                # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: