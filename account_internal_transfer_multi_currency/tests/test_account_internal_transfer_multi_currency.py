# Copyright 2026 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tests import common


class TestAccountInternalTransferMultiCurrency(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd.write({"active": True})
        cls.currency_eur.write({"active": True})

        if cls.company.currency_id == cls.currency_usd:
            cls.source_currency = cls.currency_usd
            cls.dest_currency = cls.currency_eur
        else:
            cls.source_currency = cls.currency_eur
            cls.dest_currency = cls.currency_usd

        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.dest_currency.id,
                "rate": 2.0,
                "name": fields.Date.today(),
                "company_id": cls.company.id,
            }
        )

        cls.outstanding_src = cls.env["account.account"].create(
            {
                "name": "Outstanding Src",
                "code": "101002",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        cls.outstanding_dest = cls.env["account.account"].create(
            {
                "name": "Outstanding Dest",
                "code": "101003",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )

        method_in = cls.env.ref("account.account_payment_method_manual_in")
        method_out = cls.env.ref("account.account_payment_method_manual_out")

        cls.src_journal = cls.env["account.journal"].create(
            {
                "name": "Source Bank Test",
                "code": "SRCT",
                "type": "bank",
                "currency_id": cls.source_currency.id
                if cls.source_currency != cls.company.currency_id
                else False,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_method_id": method_in.id,
                            "payment_account_id": cls.outstanding_src.id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_method_id": method_out.id,
                            "payment_account_id": cls.outstanding_src.id,
                        },
                    )
                ],
            }
        )

        cls.dest_journal = cls.env["account.journal"].create(
            {
                "name": "Destination Bank Test",
                "code": "DEST",
                "type": "bank",
                "currency_id": cls.dest_currency.id
                if cls.dest_currency != cls.company.currency_id
                else False,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "In",
                            "payment_method_id": method_in.id,
                            "payment_account_id": cls.outstanding_dest.id,
                        },
                    )
                ],
                "outbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Out",
                            "payment_method_id": method_out.id,
                            "payment_account_id": cls.outstanding_dest.id,
                        },
                    )
                ],
            }
        )

    def test_multi_currency_internal_transfer(self):
        payment = self.env["account.payment"].create(
            {
                "is_internal_transfer": True,
                "payment_type": "outbound",
                "journal_id": self.src_journal.id,
                "destination_journal_id": self.dest_journal.id,
                "amount": 100.0,
                "currency_id": self.source_currency.id,
                "date": fields.Date.today(),
                "memo": "Internal Transfer Test Memo",
            }
        )
        payment.action_post()

        paired_payment = payment.paired_internal_transfer_payment_id
        self.assertTrue(
            paired_payment, "A paired payment should have been automatically created."
        )
        self.assertEqual(paired_payment.currency_id, self.dest_currency)
        self.assertAlmostEqual(paired_payment.amount, 200.0, places=2)

        expected_memo = f"{payment.name} - {paired_payment.name}"
        self.assertEqual(payment.memo, expected_memo)
        self.assertEqual(paired_payment.memo, expected_memo)
