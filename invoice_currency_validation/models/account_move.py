# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from typing import Optional


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.onchange("currency_id")
    def _onchange_currency_set_journal(self):
        if self.currency_id:
            self.journal_id = self._find_matching_invoice_journal()
        else:
            self.journal_id = None

    def _find_matching_invoice_journal(self):
        company = self.company_id
        journal_type = (
            "sale" if self.move_type in ("out_invoice", "out_refund") else "purchase"
        )
        candidate_journals = self.env["account.journal"].search(
            [("type", "=", journal_type), ("company_id", "=", company.id),],
            order="sequence",
        )
        return next(
            (
                j
                for j in candidate_journals
                if (j.currency_id or company.currency_id) == self.currency_id
            ),
            None,
        )

    def _post(self, soft=True):
        invoices = self.filtered(lambda m: m.is_invoice())
        for invoice in invoices:
            invoice._check_invoice_currency_versus_journal_currency()

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
