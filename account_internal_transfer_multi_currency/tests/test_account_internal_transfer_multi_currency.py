# Copyright 2026 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tests import common


class TestAccountInternalTransferMultiCurrency(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Set up required data for multi-currency internal transfer testing."""
        super().setUpClass()
        cls.company = cls.env.company

        # Retrieve standard USD and EUR currencies
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")

        # Activate both currencies to ensure they can be used in transactions
        cls.currency_usd.write({"active": True})
        cls.currency_eur.write({"active": True})

        # Define source and destination currencies based on company base currency
        if cls.company.currency_id == cls.currency_usd:
            cls.source_currency = cls.currency_usd
            cls.dest_currency = cls.currency_eur
        else:
            cls.source_currency = cls.currency_eur
            cls.dest_currency = cls.currency_usd

        # Create a fixed currency rate for the destination currency
        # 1 Company Currency unit = 2 Destination Currency units
        cls.env["res.currency.rate"].create({
            "currency_id": cls.dest_currency.id,
            "rate": 2.0,
            "name": fields.Date.today(),
            "company_id": cls.company.id,
        })

        # Create source and destination bank journals with appropriate currencies
        cls.src_journal = cls.env["account.journal"].create({
            "name": "Source Bank Test",
            "code": "SRCT",
            "type": "bank",
            "currency_id": (
                cls.source_currency.id
                if cls.source_currency != cls.company.currency_id
                else False
            ),
        })
        cls.dest_journal = cls.env["account.journal"].create({
            "name": "Destination Bank Test",
            "code": "DEST",
            "type": "bank",
            "currency_id": (
                cls.dest_currency.id
                if cls.dest_currency != cls.company.currency_id
                else False
            ),
        })

        # Find a valid outstanding account to avoid ValidationError in tests
        outstanding_account = cls.env["account.account"].search([
            ("company_id", "=", cls.company.id),
            ("account_type", "=", "asset_current"),
        ], limit=1) or cls.company.transfer_account_id

        # Assign the outstanding account to all payment method lines of the test journals
        test_journals = cls.src_journal + cls.dest_journal
        method_lines = (
            test_journals.inbound_payment_method_line_ids
            + test_journals.outbound_payment_method_line_ids
        )
        method_lines.write({"payment_account_id": outstanding_account.id})

    def test_multi_currency_internal_transfer(self):
        """Test multi-currency internal transfers conversion and combined memos."""
        # Create an internal transfer payment from the source to the destination journal
        payment = self.env["account.payment"].create({
            "is_internal_transfer": True,
            "payment_type": "outbound",
            "journal_id": self.src_journal.id,
            "destination_journal_id": self.dest_journal.id,
            "amount": 100.0,
            "currency_id": self.source_currency.id,
            "date": fields.Date.today(),
            "memo": "Internal Transfer Test Memo",
        })

        # Post the payment to trigger paired payment creation and currency conversion
        payment.action_post()

        # Verify that the paired payment has been automatically created
        paired_payment = payment.paired_internal_transfer_payment_id
        self.assertTrue(
            paired_payment, "A paired payment should have been automatically created."
        )

        # Verify paired currency matches the destination journal's currency
        self.assertEqual(paired_payment.currency_id, self.dest_currency)

        # Verify the amount has been converted accurately (100.0 * 2.0 = 200.0)
        self.assertAlmostEqual(paired_payment.amount, 200.0, places=2)

        # Verify that memos on both payments are concatenated with their posted references
        expected_memo = f"{payment.name} - {paired_payment.name}"
        self.assertEqual(payment.memo, expected_memo)
        self.assertEqual(paired_payment.memo, expected_memo)
