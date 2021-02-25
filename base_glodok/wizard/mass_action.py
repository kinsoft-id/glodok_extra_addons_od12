# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, api
from odoo.models import TransientModel


class StockMoveLineMassAction(TransientModel):
    _name = 'stock.move.line.mass.action'
    _description = 'Stock Move Line Mass Action'

    def _default_stock_move_line_ids(self):
        return self.env['stock.move.line'].browse(
            self.env.context.get('active_ids'))

    stock_move_line_ids = fields.Many2many(
        string='Stock Move Line',
        comodel_name="stock.move.line",
        default=lambda self: self._default_stock_move_line_ids(),
        help="",
    )

    @api.multi
    def mass_action(self):
        self.ensure_one()
        self.stock_move_line_ids.write({'is_label_printed': True})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }