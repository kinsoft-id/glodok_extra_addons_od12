# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        for line in vals['order_line']:
            for product in line[2]:
                print(product)
        # if vals.get('warning_below_cost'):
        #     raise UserError(_('Harga jual dibawah harga cost.. Mohon ubah unit pricenya'))

        result = super(SaleOrder, self).create(vals)
        return result
