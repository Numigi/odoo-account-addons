# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountJournalExclusivity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, strict_bank_exclusivity=True))

        cls.payment_method_in = cls.env["account.payment.method"].search(
            [("payment_type", "=", "inbound")], limit=1
        )
        cls.payment_method_out = cls.env["account.payment.method"].search(
            [("payment_type", "=", "outbound")], limit=1
        )

        cls.acc_suspense_1 = cls._create_account("111310", "Suspense 1")
        cls.acc_suspense_2 = cls._create_account("111311", "Suspense 2")
        cls.acc_in_1 = cls._create_account("111320", "In 1")
        cls.acc_out_1 = cls._create_account("111321", "Out 1")
        cls.acc_shared = cls._create_account("111322", "Shared In Out")

    @classmethod
    def _create_account(cls, code, name):
        return cls.env["account.account"].create(
            {"code": code, "name": name, "account_type": "asset_current"}
        )

    def test_internal_account_exclusivity(self):
        # 1. Block sharing the same account between inbound and outbound lines
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Overlap In Out",
                    "type": "bank",
                    "code": "OVL1",
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": self.acc_shared.id,
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
                                "payment_account_id": self.acc_shared.id,
                                "payment_method_id": self.payment_method_out.id,
                            },
                        )
                    ],
                }
            )

        # 2. Block using the suspense account as an inbound payment account
        with self.assertRaises(ValidationError):
            self.env["account.journal"].create(
                {
                    "name": "Suspense In Inbound",
                    "type": "bank",
                    "code": "OVL2",
                    "suspense_account_id": self.acc_suspense_1.id,
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": self.acc_suspense_1.id,
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
                                "payment_account_id": self.acc_out_1.id,
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
                "suspense_account_id": self.acc_suspense_1.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self.acc_in_1.id,
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
                            "payment_account_id": self.acc_out_1.id,
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
                    "suspense_account_id": self.acc_suspense_1.id,  # Used by XKP1
                    "inbound_payment_method_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "In",
                                "payment_account_id": self._create_account(
                                    "991", "1"
                                ).id,
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
                                "payment_account_id": self._create_account(
                                    "992", "2"
                                ).id,
                                "payment_method_id": self.payment_method_out.id,
                            },
                        )
                    ],
                }
            )

        # 3. Create a journal in "edit" mode with a free account
        self.env["account.journal"].create(
            {
                "name": "Bank Modify Pass 1",
                "type": "bank",
                "code": "XMD2",
                "reconcile_mode": "edit",
                "suspense_account_id": self.acc_suspense_2.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self._create_account("993", "3").id,
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
                            "payment_account_id": self._create_account("994", "4").id,
                            "payment_method_id": self.payment_method_out.id,
                        },
                    )
                ],
            }
        )

        # 4. Two "edit" mode journals CAN share a suspense account
        journal_edit_2 = self.env["account.journal"].create(
            {
                "name": "Bank Modify Pass 2",
                "type": "bank",
                "code": "XMD3",
                "reconcile_mode": "edit",
                "suspense_account_id": self.acc_suspense_2.id,  # Successfully shared with XMD2
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_account_id": self._create_account("995", "5").id,
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
                            "payment_account_id": self._create_account("996", "6").id,
                            "payment_method_id": self.payment_method_out.id,
                        },
                    )
                ],
            }
        )
        self.assertTrue(journal_edit_2)
