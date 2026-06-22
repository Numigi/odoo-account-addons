# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo.exceptions import ValidationError
import pytest


@pytest.mark.common
class TestAccountJournalExclusivity(common.TransactionCase):
    def setUp(self):
        super(TestAccountJournalExclusivity, self).setUp()
        self.account_1 = self.env["account.account"].create(
            {
                "code": "111316",
                "name": "Bank Account 1",
                "account_type": "asset_cash",
            }
        )
        self.suspense_account = self.env["account.account"].create(
            {
                "code": "111312",
                "name": "Suspense Account",
                "account_type": "asset_current",
            }
        )

    def test_duplicate_bank_account_raises_error(self):
        self.env["account.journal"].create(
            {
                "name": "Bank 1",
                "code": "BNK1",
                "type": "bank",
                "default_account_id": self.account_1.id,
            }
        )
        with pytest.raises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank 2",
                    "code": "BNK2",
                    "type": "bank",
                    "default_account_id": self.account_1.id,
                }
            )

    def test_keep_suspense_mode_enforces_exclusive_suspense_account(self):
        self.env["account.journal"].create(
            {
                "name": "Bank 1",
                "code": "BNK1",
                "type": "bank",
                "reconcile_mode": "keep",
                "suspense_account_id": self.suspense_account.id,
            }
        )
        with pytest.raises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank 2",
                    "code": "BNK2",
                    "type": "bank",
                    "reconcile_mode": "keep",
                    "suspense_account_id": self.suspense_account.id,
                }
            )
