# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin = fields.Float(compute='_price_unit', readonly=True, string='Margin', store=True)

    @api.depends('price_unit')
    def _price_unit(self):
        for record in self:
            std_price = record.product_id.standard_price
            fstd_price = '{0:,.2f}'.format(std_price)
            record['margin'] = record.price_unit - std_price

            if record['margin'] < 0:
                raise UserError(_('Harga jual tidak boleh lebih dari cost.\nCost %s.') % (fstd_price))
                # return super(SaleOrderLine, self).unlink()

    @api.model
    def create(self, values):
        # print(values.product_id)
        line = super(SaleOrderLine, self).create(values)

        return line