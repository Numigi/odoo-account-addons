# -*- coding: utf-8 -*-
# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountJournalExclusivity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, strict_bank_exclusivity=True))

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
                    "name": "Bank Journal 1",
                    "type": "bank",
                    "code": "BNK1",
                }
            )

        # 2. Test successful creation with unique accounts
        journal_1 = self.env["account.journal"].create(
            {
                "name": "Bank Journal 1",
                "type": "bank",
                "code": "BNK1",
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In 1",
                            "payment_account_id": self.payment_account_1.id,
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
                    "name": "Bank Journal 2",
                    "type": "bank",
                    "code": "BNK2",
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In 2",
                                "payment_account_id": self.payment_account_1.id,
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
                            },
                        )
                    ],
                }
            )

    def test_suspense_account_exclusivity_rules(self):
        # 1. Create a journal in "keep" mode
        self.env["account.journal"].create(
            {
                "name": "Bank Keep",
                "type": "bank",
                "code": "KEEP",
                "reconcile_mode": "keep",
                "suspense_account_id": self.suspense_account_1.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {"name": "In", "payment_account_id": self.payment_account_1.id},
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_account_id": self.payment_account_2.id,
                        },
                    )
                ],
            }
        )

        # 2. A "modify" mode journal CANNOT use a "keep" mode suspense account
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Bank Modify 1",
                    "type": "bank",
                    "code": "MOD1",
                    "reconcile_mode": "modify",
                    "suspense_account_id": self.suspense_account_1.id,  # Used by keep
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": self.suspense_account_2.id,
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
                            },
                        )
                    ],
                }
            )

        # 3. Create a journal in "modify" mode with a free account
        journal_mod_1 = self.env["account.journal"].create(
            {
                "name": "Bank Modify 1",
                "type": "bank",
                "code": "MOD1",
                "reconcile_mode": "modify",
                "suspense_account_id": self.suspense_account_2.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self.env["account.account"]
                            .create({"code": "9991", "name": "x"})
                            .id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_account_id": self.env["account.account"]
                            .create({"code": "9992", "name": "x"})
                            .id,
                        },
                    )
                ],
            }
        )

        # 4. A "modify" mode journal CAN share an account with another "modify" mode journal
        journal_mod_2 = self.env["account.journal"].create(
            {
                "name": "Bank Modify 2",
                "type": "bank",
                "code": "MOD2",
                "reconcile_mode": "modify",
                "suspense_account_id": self.suspense_account_2.id,  # Shared with MOD1
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self.env["account.account"]
                            .create({"code": "9993", "name": "x"})
                            .id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_account_id": self.env["account.account"]
                            .create({"code": "9994", "name": "x"})
                            .id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            journal_mod_1.suspense_account_id, journal_mod_2.suspense_account_id
        )
