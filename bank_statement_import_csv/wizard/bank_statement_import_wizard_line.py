# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
    has_error = fields.Boolean()

    def validate_error_correction(self):
        self.has_error = False
        return self.wizard_id.get_wizard_action()

    def _get_statement_line_vals(self):
        currency = self._get_currency()
        return {
            "date": datetime.strptime(self.date, "%Y-%m-%d").date(),
            "name": self.description,
            "ref": self.reference,
            "amount": float(self.amount) if self.amount else None,
            "amount_currency": float(self.currency_amount) if currency else None,
            "currency_id": currency.id if currency else None,
        }

    def _get_currency(self):
        journal = self.wizard_id.journal_id
        journal_currency = journal.currency_id or journal.company_id.currency_id
        currency_required = self.currency and self.currency != journal_currency.name
        if currency_required:
            return self._find_currency_from_code()

    def _find_currency_from_code(self):
        currency = self.env["res.currency"].search(
            [("name", "=", self.currency)], limit=1
        )
        if not currency:
            raise ValidationError(
                _("No active currency found with the code {}.".format(self.currency))
            )
        return currency
