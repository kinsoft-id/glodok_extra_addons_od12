# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


class SaleAdvPaymentInv(models.TransientModel):
	_inherit = 'sale.advance.payment.inv'

	@api.multi
	def _create_invoice(self, order, so_line, amount):
		inv_obj = self.env['account.invoice']
		ir_property_obj = self.env['ir.property']

		account_id = False
		if self.product_id.id:
			account_id = self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id
		if not account_id:
			inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
			account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
		if not account_id:
			raise UserError(
				_('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
				(self.product_id.name,))

		if self.amount <= 0.00:
			raise UserError(_('The value of the down payment amount must be positive.'))
		context = {'lang': order.partner_id.lang}
		if self.advance_payment_method == 'percentage':
			amount = order.amount_untaxed * self.amount / 100
			name = _("Down payment of %s%%") % (self.amount,)
		else:
			amount = self.amount
			name = _('Down Payment')

			import re
			# name += "\n%s" % ("\n".join(order.order_line.filtered(lambda r:re.compile('!('+_('Down Payment')+')').search(r.name)).mapped(lambda r:"* %s (%s) %s" %(r.product_uom_qty,r.product_uom.name, r.product_id.display_name))))
			p = re.compile("(Down Payment|Advance\:)")
			for ll in order.order_line:
				# _logger.critical(ll.name)
				# _logger.critical(p.search(ll.name))
				if p.search(ll.name) == None:
					name += "\n* %s %s - %s" % (ll.product_uom_qty,ll.product_uom.name, ll.product_id.display_name, )
		del context
		taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
		if order.fiscal_position_id and taxes:
			tax_ids = order.fiscal_position_id.map_tax(taxes).ids
		else:
			tax_ids = taxes.ids

		invoice = inv_obj.create({
			'name': order.client_order_ref or order.name,
			'origin': order.name,
			'type': 'out_invoice',
			'reference': False,
			'account_id': order.partner_id.property_account_receivable_id.id,
			'partner_id': order.partner_invoice_id.id,
			'partner_shipping_id': order.partner_shipping_id.id,
			'invoice_line_ids': [(0, 0, {
				'name': name,
				'origin': order.name,
				'account_id': account_id,
				'price_unit': amount,
				'quantity': 1.0,
				'discount': 0.0,
				'uom_id': self.product_id.uom_id.id,
				'product_id': self.product_id.id,
				'sale_line_ids': [(6, 0, [so_line.id])],
				'invoice_line_tax_ids': [(6, 0, tax_ids)],
				'account_analytic_id': order.analytic_account_id.id or False,
			})],
			'currency_id': order.pricelist_id.currency_id.id,
			'payment_term_id': order.payment_term_id.id,
			'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
			'team_id': order.team_id.id,
			'user_id': order.user_id.id,
			'comment': order.note,
		})
		invoice.compute_taxes()
		invoice.message_post_with_view('mail.message_origin_link',
					values={'self': invoice, 'origin': order},
					subtype_id=self.env.ref('mail.mt_note').id)
		return invoice

class AccountInvoice(models.Model):

	_inherit = 'account.invoice'

	def get_words(self, amount):
		from num2words import num2words
		# _logger.critical(self._context)
		amount_text = "%s %s" % (num2words(amount, lang='id').replace('koma nol',''),'Rupiah')

		return amount_text.title()
		# return self.currency_id.amount_to_text(amount)
		# _logger.critical(self._context)
		# return self.currency_id.amount_to_text(amount)
		# return self.amount_to_text(amount)

	def invoice_print(self):

		# return super(AccountInvoice, self).invoice_print()
		res = self.env.ref('base_glodok.action_report_invoice_a6').report_action(self)
		return res