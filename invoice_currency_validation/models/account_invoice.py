# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        journal_currency = (
            self.journal_id.currency_id or
            self.journal_id.company_id.currency_id)

        if journal_currency != self.currency_id:
            journal_type = 'sale' if self.type == 'out_invoice' else 'purchase'
            journal_id = self.env['account.journal'].search([
                ('type', '=', journal_type),
                '|',
                ('currency_id', '=', self.currency_id.id),
                ('currency_id', '=', False)
            ], order='sequence', limit=1)

            if journal_id:
                self.journal_id = journal_id

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            invoice._check_currency()

        return super(AccountInvoice, self).action_invoice_open()

    def _check_currency(self):
        invoice_currency = self.currency_id
        journal_currency = self.journal_id.currency_id
        account_currency = self.account_id.currency_id
        company_currency = self.company_id.currency_id

        if not journal_currency and not account_currency:
            return

        if (
            journal_currency and not account_currency and
            journal_currency != company_currency
        ):
            raise UserError(_(
                "The invoice %(invoice_name)s could not be validated. "
                "The selected journal (%(journal_name)s) has a currency "
                "(%(journal_currency)s) and the selected account "
                "(%(account_code)s) has no currency.") % {
                    'invoice_name': self.display_name,
                    'journal_name': self.journal_id.name,
                    'journal_currency': journal_currency.name,
                    'account_code': self.account_id.code,
            })

        if (
            not journal_currency and account_currency and
            account_currency != company_currency
        ):
            raise UserError(_(
                "The invoice %(invoice_name)s could not be validated. "
                "The selected journal (%(journal_name)s) has no currency "
                "and the selected account (%(account_code)s) has a "
                "currency (%(account_currency)s).") % {
                    'invoice_name': self.display_name,
                    'journal_name': self.journal_id.name,
                    'account_code': self.account_id.code,
                    'account_currency': account_currency.name,
            })

        if (
            journal_currency and account_currency and
            journal_currency != account_currency
        ):
            raise UserError(_(
                "The invoice %(invoice_name)s could not be validated. "
                "The selected journal (%(journal_name)s) has a currency "
                "(%(journal_currency)s) and the selected account "
                "(%(account_code)s) has a currency "
                "(%(account_currency)s).") % {
                    'invoice_name': self.display_name,
                    'journal_name': self.journal_id.name,
                    'journal_currency': journal_currency.name,
                    'account_code': self.account_id.code,
                    'account_currency': account_currency.name,
            })

        if (journal_currency or company_currency) != invoice_currency:
            raise UserError(_(
                "The invoice %(invoice_name)s could not be validated. "
                "The selected journal (%(journal_name)s) has a currency "
                "(%(journal_currency)s) and the invoice has a currency "
                "(%(invoice_currency)s).") % {
                    'invoice_name': self.display_name,
                    'journal_name': self.journal_id.name,
                    'journal_currency': journal_currency.name,
                    'invoice_currency': invoice_currency.name,
            })
