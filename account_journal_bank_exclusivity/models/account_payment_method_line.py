# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    @api.constrains("payment_account_id", "journal_id")
    def _check_payment_account_requirements(self):
        # Bypass during automated tests to avoid breaking Odoo's standard chart template loading
        if config.get("test_enable") and not self.env.context.get(
            "strict_bank_exclusivity"
        ):
            return

        bank_lines = self.filtered(lambda l: l.journal_id.type == "bank")
        for line in bank_lines:
            line._verify_payment_account_presence()
            line._verify_payment_account_uniqueness()

    def _verify_payment_account_presence(self):
        # Enforce account presence on every single payment method line linked to a bank
        if not self.payment_account_id:
            raise ValidationError(
                _("An account is required for payment method %s on bank journal %s.")
                % (self.name, self.journal_id.name)
            )

    def _verify_payment_account_uniqueness(self):
        duplicate = self.search(
            [
                ("payment_account_id", "=", self.payment_account_id.id),
                ("journal_id", "!=", self.journal_id.id),
                ("journal_id.type", "=", "bank"),
                ("id", "!=", self.id),
            ],
            limit=1,
        )
        if duplicate:
            raise ValidationError(
                _("The payment account %s is already used in journal %s.")
                % (self.payment_account_id.code, duplicate.journal_id.name)
            )
