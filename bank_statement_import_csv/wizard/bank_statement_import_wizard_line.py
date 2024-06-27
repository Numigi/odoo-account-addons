# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from ..loader import (
    parse_decimal_or_error,
    parse_currency_or_error,
    parse_date_or_error,
)
from ..error import is_bank_statement_error


class BankStatementImportWizardLine(models.TransientModel):

    _name = "bank.statement.import.wizard.line"
    _description = "Bank Statement Import Wizard Line"

    wizard_id = fields.Many2one(
        "bank.statement.import.wizard", required=True, ondelete="cascade"
    )
    date = fields.Char()
    amount = fields.Char()
    currency = fields.Char()
    currency_amount = fields.Char()
    balance = fields.Char()
    description = fields.Char()
    reference = fields.Char()
    partner_name = fields.Char()
    has_error = fields.Boolean()

    def validate_error_correction(self):
        self.has_error = False
        self._validate_line_fields()
        return self.wizard_id.get_wizard_action()

    def _validate_line_fields(self):
        for field in ("amount", "currency_amount", "balance"):
            self._validate_line_amount(field)

        self._validate_line_date()
        self._validate_line_currency()

    def _validate_line_amount(self, field):
        value = self[field]
        if value:
            parsed_value = parse_decimal_or_error(value)
            self._raise_if_is_bank_statement_error(parsed_value)

    def _validate_line_date(self):
        parsed_value = parse_date_or_error(self.date, "%Y-%m-%d")
        self._raise_if_is_bank_statement_error(parsed_value)

    def _validate_line_currency(self):
        code = self.currency
        if code:
            value = parse_currency_or_error(code)
            self._raise_if_is_bank_statement_error(value)

    def _raise_if_is_bank_statement_error(self, value):
        if is_bank_statement_error(value):
            raise ValidationError(_(value.msg).format(
                *value.args, **value.kwargs))

    def _get_statement_line_vals(self):
        currency = self._get_currency()
        return {
            "date": datetime.strptime(self.date, "%Y-%m-%d").date(),
            "payment_ref": self.description,
            "ref": self.reference,
            "partner_name": self.partner_name,
            "amount": float(self.amount) if self.amount else None,
            "amount_currency": float(self.currency_amount) if currency else None,
            "foreign_currency_id": currency.id if currency else None,
        }

    def _get_currency(self):
        journal = self.wizard_id.journal_id
        journal_currency = journal.currency_id or journal.company_id.currency_id
        currency_required = self.currency and self.currency != journal_currency.name
        if currency_required:
            return self._find_currency_from_code()
        return False

    def _find_currency_from_code(self):
        currency = self.env["res.currency"].search(
            [("name", "=", self.currency)], limit=1
        )
        if not currency:
            raise ValidationError(
                _("No active currency found with the code {}.".format(self.currency))
            )
        return currency
