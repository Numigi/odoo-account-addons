# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.journal_id.currency_id != self.currency_id:
            journal_type = 'sale' if self.type == 'out_invoice' else 'purchase'

            journal_id = self.env['account.journal'].search([
                ('type', '=', journal_type),
                ('currency_id', '=', self.currency_id.id)
            ], order='sequence', limit=1)
            if journal_id:
                self.journal_id = journal_id

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            invoice_currency = invoice.currency_id
            journal_currency = invoice.journal_id.currency_id
            account_currency = invoice.account_id.currency_id

            # What if journal_currency and account_currency are both null ?

            if journal_currency and not account_currency:
                raise UserError(_(
                    "The invoice %(invoice_name)s could not be validated. "
                    "The selected journal (%(journal_name)s) has a currency "
                    "(%(journal_currency)s) and the selected account "
                    "(%(account_code)s) has no currency.") % {
                        'invoice_name': invoice.display_name,
                        'journal_name': invoice.journal_id.name,
                        'journal_currency': journal_currency.name,
                        'account_code': invoice.account_id.code,
                })

            if not journal_currency and account_currency:
                raise UserError(_(
                    "The invoice %(invoice_name)s could not be validated. "
                    "The selected journal (%(journal_name)s) has no currency "
                    "and the selected account (%(account_code)s) has a "
                    "currency (%(account_currency)s).") % {
                        'invoice_name': invoice.display_name,
                        'journal_name': invoice.journal_id.name,
                        'account_code': invoice.account_id.code,
                        'account_currency': account_currency.name,
                })

            if journal_currency != account_currency:
                raise UserError(_(
                    "The invoice %(invoice_name)s could not be validated. "
                    "The selected journal (%(journal_name)s) has a currency "
                    "(%(journal_currency)s) and the selected account "
                    "(%(account_code)s) has a currency "
                    "(%(account_currency)s).") % {
                        'invoice_name': invoice.display_name,
                        'journal_name': invoice.journal_id.name,
                        'journal_currency': journal_currency.name,
                        'account_code': invoice.account_id.code,
                        'account_currency': account_currency.name,
                })

            if journal_currency != invoice_currency:
                raise UserError(_(
                    "The invoice %(invoice_name)s could not be validated. "
                    "The selected journal (%(journal_name)s) has a currency "
                    "(%(journal_currency)s) and the invoice has a currency "
                    "(%(invoice_currency)s).") % {
                        'invoice_name': invoice.display_name,
                        'journal_name': invoice.journal_id.name,
                        'journal_currency': journal_currency.name,
                        'invoice_currency': invoice_currency.name,
                })

        return super(AccountInvoice, self).action_invoice_open()
