# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin = fields.Float(compute='_compute_margin', inverse="_inverse_margin", readonly=False, string='Margin', store=True)

    @api.depends('price_unit')
    def _compute_margin(self):
        for record in self:
            std_price = record.product_id.standard_price
            fstd_price = '{0:,.2f}'.format(std_price)
            record['margin'] = record.price_unit - std_price

    def _inverse_margin(self):
        for record in self:
            if not record.margin:
                continue

    @api.model
    def create(self, values):
        # print(values.product_id)
        line = super(SaleOrderLine, self).create(values)

        return line