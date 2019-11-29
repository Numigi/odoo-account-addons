# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from typing import Optional


def _find_matching_invoice_journal(
    company: 'res.company',
    invoice_type: str,
    invoice_currency: 'res.currency',
) -> Optional['account.journal']:
    """Find a matching journal given a type of invoice and a currency.

    :param company: the company of the invoice
    :param invoice_type: the type of invoice
    :param invoice_currency: the invoice currency
    :return: the first matching journal if any found
    """
    journal_type = (
        'sale' if invoice_type in ('out_invoice', 'out_refund') else 'purchase'
    )
    candidate_journals = company.env['account.journal'].search([
        ('type', '=', journal_type),
        ('company_id', '=', company.id),
    ], order='sequence')
    return next((
        j for j in candidate_journals
        if (j.currency_id or company.currency_id) == invoice_currency
    ), None)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.onchange('currency_id')
    def _onchange_currency_set_journal(self):
        if self.currency_id:
            self.journal_id = _find_matching_invoice_journal(
                self.company_id, self.type, self.currency_id
            )
        else:
            self.journal_id = None

    def _check_invoice_currency_versus_journal_currency(self):
        company_currency = self.company_id.currency_id
        invoice_currency = self.currency_id or company_currency
        journal_currency = self.journal_id.currency_id or company_currency

        if journal_currency != invoice_currency:
            raise UserError(_(
                "The invoice could not be validated. "
                "The invoice is in currency {invoice_currency} "
                "and the selected journal ({journal}) is in "
                "currency {journal_currency}."
            ).format(
                invoice=self.display_name,
                invoice_currency=invoice_currency.display_name,
                journal=self.journal_id.display_name,
                journal_currency=journal_currency.name,
            ))

    def _check_invoice_currency_versus_account_currency(self):
        company_currency = self.company_id.currency_id
        invoice_currency = self.currency_id or company_currency
        account_currency = self.account_id.currency_id or company_currency

        if account_currency != invoice_currency:
            raise UserError(_(
                "The invoice could not be validated. "
                "The invoice is in currency {invoice_currency} "
                "and the selected account ({account}) is in "
                "currency {account_currency}."
            ).format(
                invoice=self.display_name,
                invoice_currency=invoice_currency.display_name,
                account=self.account_id.display_name,
                account_currency=account_currency.name,
            ))

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            invoice._check_invoice_currency_versus_journal_currency()
            invoice._check_invoice_currency_versus_account_currency()

        return super().action_invoice_open()
