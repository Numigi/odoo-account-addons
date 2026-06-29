# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_payment_account_required()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self._check_payment_account_required()
        return res

    def _check_payment_account_required(self):
        # On bank journals, every payment method line must define an account
        for line in self:
            if line.journal_id.type == "bank" and not line.payment_account_id:
                raise ValidationError(
                    _(
                        "An account is required for payment method %s "
                        "on bank journal %s."
                    )
                    % (line.name, line.journal_id.name)
                )

    @api.constrains("payment_account_id", "journal_id")
    def _check_payment_account_uniqueness(self):
        # Only verify uniqueness for bank lines that actually have an account set
        bank_lines = self.filtered(
            lambda l: l.journal_id.type == "bank" and l.payment_account_id
        )
        for line in bank_lines:
            line._verify_payment_account_exclusivity()

    def _verify_payment_account_exclusivity(self):
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
