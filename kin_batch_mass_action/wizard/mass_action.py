# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, api
from odoo.models import TransientModel


class StockPickingBatchMassAction(TransientModel):
    _name = 'stock.picking.batch.mass.action'
    _description = 'Stock Picking Batch Mass Action'

    def _default_picking_batch_ids(self):
        return self.env['stock.picking.batch'].browse(
            self.env.context.get('active_ids'))

    picking_batch_ids = fields.Many2many(
        string='Pickings Batch',
        comodel_name="stock.picking.batch",
        default=lambda self: self._default_picking_batch_ids(),
        help="",
    )

    @api.multi
    def mass_action(self):
        self.ensure_one()

        assigned_picking_batch_lst = self.picking_batch_ids.\
            filtered(lambda x: x.state not in ('done', 'cancel')).\
            sorted(key=lambda r: r.send_time)

        assigned_picking_lst = assigned_picking_batch_lst.mapped('picking_ids').filtered(
                lambda m: m.state not in ('done', 'cancel'))

        if assigned_picking_lst:
            assigned_picking_lst.write({'delivery_status':'received'})

            assigned_move_line = assigned_picking_lst.mapped('move_line_ids').filtered(
                lambda m: m.state not in ('done', 'cancel'))

            if assigned_move_line:
                for move_line in assigned_move_line:
                    move_line.write({'pickup_validated': True, 'pickup_validated_by': self.env.uid, 'pickup_qty': move_line.qty_done})

                quantities_done = sum(
                    move_line.qty_done for move_line in assigned_move_line
                    )
                if not quantities_done:
                    return assigned_picking_lst.action_immediate_transfer_wizard()

            if assigned_picking_lst._check_backorder():
                return assigned_picking_lst.action_generate_backorder_wizard()

            assigned_picking_lst.action_done()

        assigned_picking_batch_lst.done()
