# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin = fields.Float(compute='_compute_margin', inverse="_inverse_margin", readonly=False, string='Margin', store=True)
    margin_subtotal = fields.Float(compute='_compute_margin_subtotal', inverse="_inverse_margin_subtotal", readonly=False, string='Margin Subtotal', store=True)
    
    order_ref = fields.Char('Customer Reference', related='order_id.client_order_ref')
    customer_id = fields.Many2one('res.partner', related='order_id.partner_id')
    order_date = fields.Datetime('Order Date', related='order_id.confirmation_date')
    is_cancel = fields.Boolean('Is Cancel', related='order_id.is_cancel')

    @api.depends('price_unit')
    def _compute_margin(self):
        for record in self:
            std_price = record.product_id.standard_price
            fstd_price = '{0:,.2f}'.format(std_price)
            record['margin'] = record.price_unit - std_price

    @api.depends('margin')
    def _compute_margin_subtotal(self):
        for record in self:
            record['margin_subtotal'] = record.margin * record.product_uom_qty

    def _inverse_margin(self):
        for record in self:
            if not record.margin:
                continue

    def _inverse_margin_subtotal(self):
        for record in self:
            if not record.margin:
                continue

    @api.model
    def create(self, values):
        # print(values.product_id)
        line = super(SaleOrderLine, self).create(values)

        return line