# models/delivery_order.py
from odoo import models, api
import subprocess

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def print_delivery_order(self):
        for picking in self:
            # Generate the delivery order text
            delivery_order_text = self._generate_delivery_order_text(picking)
            # Send to printer
            self._send_to_printer(delivery_order_text)

    def _generate_delivery_order_text(self, picking):
        lines = []
        lines.append(f"Delivery Order: {picking.name}")
        lines.append(f"Date: {picking.scheduled_date}")
        lines.append(f"Customer: {picking.partner_id.name}")
        lines.append("\nItems:")
        for line in picking.move_lines:
            lines.append(f"{line.product_id.name}: {line.product_uom_qty} {line.product_uom.name}")
        return "\n".join(lines)

    def _send_to_printer(self, text):
        printer_ip = '192.168.1.100'  # Replace with your printer's IP address
        printer_name = 'LX_300'  # Replace with your printer's name if necessary
        try:
            # Create a temporary file with the delivery order text
            with open('/tmp/delivery_order.txt', 'w') as f:
                f.write(text)
            # Send the file to the printer using lpr
            subprocess.run(['lpr', '-H', printer_ip, '/tmp/delivery_order.txt'], check=True)
        except Exception as e:
            # Log the error
            _logger.error(f"Failed to send delivery order to printer: {e}")
