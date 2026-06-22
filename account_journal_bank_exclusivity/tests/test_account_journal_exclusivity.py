# Copyright 2026 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import ValidationError
import pytest


@pytest.mark.common
class TestAccountJournalExclusivity(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.account_1 = self._create_account("111316", "Bank Account 1", "asset_cash")
        self.account_2 = self._create_account("111317", "Bank Account 2", "asset_cash")
        self.suspense_1 = self._create_account("111312", "Suspense 1", "asset_current")
        self.suspense_2 = self._create_account("111313", "Suspense 2", "asset_current")

        self.in_method = self.env.ref("account.account_payment_method_manual_in")
        self.out_method = self.env.ref("account.account_payment_method_manual_out")

    def _create_account(self, code, name, account_type):
        return self.env["account.account"].create(
            {
                "code": code,
                "name": name,
                "account_type": account_type,
                "company_ids": [(4, self.company.id)],
            }
        )

    def _get_journal_vals(self, name, code, default_acc, suspense_acc, mode="modify"):
        return {
            "name": name,
            "code": code,
            "type": "bank",
            "default_account_id": default_acc.id,
            "reconcile_mode": mode,
            "suspense_account_id": suspense_acc.id,
            "inbound_payment_method_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "In",
                        "payment_method_id": self.in_method.id,
                        "payment_account_id": suspense_acc.id,
                    },
                )
            ],
            "outbound_payment_method_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Out",
                        "payment_method_id": self.out_method.id,
                        "payment_account_id": suspense_acc.id,
                    },
                )
            ],
        }

    def test_duplicate_bank_account_raises_error(self):
        vals1 = self._get_journal_vals(
            "Bank 1", "BNK1", self.account_1, self.suspense_1
        )
        self.env["account.journal"].create(vals1)

        vals2 = self._get_journal_vals(
            "Bank 2", "BNK2", self.account_1, self.suspense_2
        )
        with pytest.raises(ValidationError):
            self.env["account.journal"].create(vals2)

    def test_keep_suspense_mode_enforces_exclusive_suspense_account(self):
        vals1 = self._get_journal_vals(
            "Bank 3", "BNK3", self.account_1, self.suspense_1, "keep"
        )
        self.env["account.journal"].create(vals1)

        vals2 = self._get_journal_vals(
            "Bank 4", "BNK4", self.account_2, self.suspense_1, "keep"
        )
        with pytest.raises(ValidationError):
            self.env["account.journal"].create(vals2)
