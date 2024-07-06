from odoo import _, api
from odoo.models import Model
from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)


class StockPicking(Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        # _logger.info(vals.get('picking_type_id'))
        if vals.get('picking_type_id') == 1:
            if self.env.user.has_group('kin_sme_customize.group_create_do'):
                return super(StockPicking, self).create(vals)
            else:
                raise AccessError("You do not have the necessary permissions to create delivery order.")
        else:
            return super(StockPicking, self).create(vals)
        