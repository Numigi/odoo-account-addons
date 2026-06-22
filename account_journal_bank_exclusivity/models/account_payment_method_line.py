# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    @api.constrains("payment_account_id")
    def _check_payment_account_uniqueness(self):
        lines = self.filtered(
            lambda l: l.journal_id.type == "bank" and l.payment_account_id
        )
        for line in lines:
            self._verify_line_account_uniqueness(line)

    def _verify_line_account_uniqueness(self, line):
        duplicate = self.search(
            [
                ("payment_account_id", "=", line.payment_account_id.id),
                ("journal_id", "!=", line.journal_id.id),
                ("journal_id.type", "=", "bank"),
            ],
            limit=1,
        )
        if duplicate:
            raise ValidationError(
                _("The payment account %s is already used in journal %s.")
                % (line.payment_account_id.code, duplicate.journal_id.name)
            )
