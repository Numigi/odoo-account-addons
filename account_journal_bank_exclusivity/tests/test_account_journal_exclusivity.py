# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountJournalExclusivity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, strict_bank_exclusivity=True))

        # Find standard payment methods required by Odoo 18 data models
        cls.payment_method_in = cls.env["account.payment.method"].search(
            [("payment_type", "=", "inbound")], limit=1
        )
        cls.payment_method_out = cls.env["account.payment.method"].search(
            [("payment_type", "=", "outbound")], limit=1
        )

        # Create base accounts for testing
        cls.suspense_account_1 = cls.env["account.account"].create(
            {
                "code": "111310",
                "name": "Suspense Account 1",
                "account_type": "asset_current",
            }
        )
        cls.suspense_account_2 = cls.env["account.account"].create(
            {
                "code": "111311",
                "name": "Suspense Account 2",
                "account_type": "asset_current",
            }
        )
        cls.payment_account_1 = cls.env["account.account"].create(
            {
                "code": "111320",
                "name": "Payment Account 1",
                "account_type": "asset_current",
            }
        )
        cls.payment_account_2 = cls.env["account.account"].create(
            {
                "code": "111321",
                "name": "Payment Account 2",
                "account_type": "asset_current",
            }
        )

    def test_payment_account_mandatory_and_unique(self):
        # 1. Test missing payment accounts
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank Journal Unique 1",
                    "type": "bank",
                    "code": "TXB1",
                }
            )

        # 2. Test successful creation with unique accounts and valid payment methods
        journal_1 = self.env["account.journal"].create(
            {
                "name": "Bank Journal Unique 1",
                "type": "bank",
                "code": "TXB1",
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In 1",
                            "payment_account_id": self.payment_account_1.id,
                            "payment_method_id": self.payment_method_in.id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out 1",
                            "payment_account_id": self.payment_account_2.id,
                            "payment_method_id": self.payment_method_out.id,
                        },
                    )
                ],
            }
        )
        self.assertTrue(journal_1)

        # 3. Test uniqueness constraint failure
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank Journal Unique 2",
                    "type": "bank",
                    "code": "TXB2",
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In 2",
                                "payment_account_id": self.payment_account_1.id,  # Duplicate
                                "payment_method_id": self.payment_method_in.id,
                            },
                        )
                    ],
                    "outbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Out 2",
                                "payment_account_id": self.suspense_account_2.id,
                                "payment_method_id": self.payment_method_out.id,
                            },
                        )
                    ],
                }
            )

    def test_suspense_account_exclusivity_rules(self):
        # 1. Create a base journal in "keep" mode
        self.env["account.journal"].create(
            {
                "name": "Bank Keep",
                "type": "bank",
                "code": "XKP1",
                "reconcile_mode": "keep",
                "suspense_account_id": self.suspense_account_1.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self.payment_account_1.id,
                            "payment_method_id": self.payment_method_in.id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_account_id": self.payment_account_2.id,
                            "payment_method_id": self.payment_method_out.id,
                        },
                    )
                ],
            }
        )

        # 2. An "edit" mode journal CANNOT use a "keep" mode suspense account
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank Modify Fail",
                    "type": "bank",
                    "code": "XMD1",
                    "reconcile_mode": "edit",
                    "suspense_account_id": self.suspense_account_1.id,  # Used by XKP1
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": self.suspense_account_2.id,
                                "payment_method_id": self.payment_method_in.id,
                            },
                        )
                    ],
                    "outbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Out",
                                "payment_account_id": self.suspense_account_2.id,
                                "payment_method_id": self.payment_method_out.id,
                            },
                        )
                    ],
                }
            )

        # 3. Create a journal in "edit" mode with a free account
        free_account_1 = self.env["account.account"].create(
            {"code": "9991", "name": "Free 1", "account_type": "asset_current"}
        )
        free_account_2 = self.env["account.account"].create(
            {"code": "9992", "name": "Free 2", "asset_current": "asset_current"}
        )

        self.env["account.journal"].create(
            {
                "name": "Bank Modify Pass 1",
                "type": "bank",
                "code": "XMD2",
                "reconcile_mode": "edit",
                "suspense_account_id": self.suspense_account_2.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": free_account_1.id,
                            "payment_method_id": self.payment_method_in.id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_account_id": free_account_2.id,
                            "payment_method_id": self.payment_method_out.id,
                        },
                    )
                ],
            }
        )

        # UPDATED: 4. Two "edit" mode journals CANNOT share a suspense account anymore
        free_account_3 = self.env["account.account"].create(
            {"code": "9993", "name": "Free 3", "account_type": "asset_current"}
        )
        free_account_4 = self.env["account.account"].create(
            {"code": "9994", "name": "Free 4", "account_type": "asset_current"}
        )

        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank Modify Pass 2",
                    "type": "bank",
                    "code": "XMD3",
                    "reconcile_mode": "edit",
                    "suspense_account_id": self.suspense_account_2.id,
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": free_account_3.id,
                                "payment_method_id": self.payment_method_in.id,
                            },
                        )
                    ],
                    "outbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Out",
                                "payment_account_id": free_account_4.id,
                                "payment_method_id": self.payment_method_out.id,
                            },
                        )
                    ],
                }
            )
