# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, *args, **kwargs):
        res = super().process_reconciliation(*args, **kwargs)

        if self.journal_id.use_transit_account:
            payments = self._get_transit_eft_payments()
            payments.write({"state": "reconciled"})

        return res

    def button_cancel_reconciliation(self):
        if self.journal_id.use_transit_account:
            payments = self._get_transit_eft_payments()
            payments.write({"state": "sent"})

        super().button_cancel_reconciliation()

    def _get_transit_eft_payments(self):
        payments = self.mapped(
            "journal_entry_ids.move_id.line_ids"
            ".matched_credit_ids.credit_move_id.payment_id"
        )
        return payments.filtered("is_eft_payment")
