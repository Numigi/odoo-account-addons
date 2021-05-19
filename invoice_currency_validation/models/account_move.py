# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from typing import Optional


class AccountMove(models.Model):

    _inherit = "account.move"

    def _post(self, soft=True):
        invoices = self.filtered(lambda m: m.is_invoice())
        for invoice in invoices:
            invoice._check_invoice_currency_versus_journal_currency()
            invoice._check_invoice_currency_versus_account_currency()

        return super()._post()

    def _check_invoice_currency_versus_journal_currency(self):
        company_currency = self.company_id.currency_id
        invoice_currency = self.currency_id or company_currency
        journal_currency = self.journal_id.currency_id or company_currency

        if journal_currency != invoice_currency:
            raise UserError(
                _(
                    "The invoice could not be validated. "
                    "The invoice is in currency {invoice_currency} "
                    "and the selected journal ({journal}) is in "
                    "currency {journal_currency}."
                ).format(
                    invoice=self.display_name,
                    invoice_currency=invoice_currency.display_name,
                    journal=self.journal_id.display_name,
                    journal_currency=journal_currency.name,
                )
            )

    def _check_invoice_currency_versus_account_currency(self):
        company_currency = self.company_id.currency_id
        invoice_currency = self.currency_id or company_currency

        partner_lines = self.line_ids.filtered(
            lambda l: l.account_id.internal_type in (
                "receivable",
                "payable",
            )
        )

        for line in partner_lines:
            account_currency = line.account_id.currency_id or company_currency
            if account_currency != invoice_currency:
                raise UserError(
                    _(
                        "The invoice could not be validated. "
                        "The invoice is in currency {invoice_currency} "
                        "and the selected account ({account}) is in "
                        "currency {account_currency}."
                    ).format(
                        invoice=self.display_name,
                        invoice_currency=invoice_currency.display_name,
                        account=line.account_id.display_name,
                        account_currency=account_currency.name,
                    )
                )
