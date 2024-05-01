# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import pytest
from contextlib import contextmanager
from datetime import datetime, timedelta
from odoo import fields
from odoo.tests import common
from odoo.exceptions import ValidationError
from unittest.mock import patch


class TestStripe(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_key = "myapikey"

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Stripe",
                "type": "bank",
                "code": "STRI",
                "currency_id": cls.env.ref("base.CAD").id,
            }
        )

        cls.provider = cls.env["online.bank.statement.provider"].create(
            {
                "journal_id": cls.journal.id,
                "service": "stripe",
                "stripe_api_key": cls.api_key,
            }
        )

        cls.datetime_from = datetime.now() - timedelta(30)
        cls.datetime_to = cls.datetime_from + timedelta(15)

        cls.transaction_date = fields.Date.context_today(
            cls.env.user, cls.datetime_from
        )

        cls.email = "teststripe@example.com"
        cls.partner_name = "Johnny Go"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": cls.partner_name,
                "email": cls.email,
            }
        )

    def setUp(self):
        super().setUp()
        self.reference = "SO91234"
        self.transaction_id = "txn_1"
        self.transaction = {
            "id": self.transaction_id,
            "created": int(self.datetime_from.timestamp()),
            "object": "balance_transaction",
            "description": self.reference,
            "amount": 1000,
            "fee": 40,
            "source": {
                "billing_details": {
                    "email": self.email,
                    "name": self.partner_name,
                }
            },
            "status": "available",
        }
        self.transactions = [self.transaction]
        self.balance = 3000

    def test_map_transaction(self):
        vals = self.provider._map_stripe_transaction(self.transaction)
        assert json.loads(vals["stripe_payload"]) == self.transaction
        assert self.reference in vals["name"]
        assert self.reference in vals["narration"]
        assert vals["ref"] == self.reference
        assert vals["amount"] == 10
        assert vals["partner_id"] == self.partner.id
        assert vals["partner_name"] == f"{self.partner_name} ({self.email})"
        assert vals["date"] == self.transaction_date

    def test_map_fee(self):
        vals = self.provider._map_stripe_fee(self.transaction)
        assert json.loads(vals["stripe_payload"]) == self.transaction
        assert self.reference in vals["name"]
        assert self.reference in vals["narration"]
        assert vals["ref"] == self.reference
        assert vals["amount"] == -0.40
        assert vals["partner_id"] == self.partner.id
        assert vals["partner_name"] == f"{self.partner_name} ({self.email})"
        assert vals["date"] == self.transaction_date

    def test_no_partner_email(self):
        self.transaction["source"]["billing_details"]["email"] = None
        vals = self.provider._map_stripe_transaction(self.transaction)
        self.assertIsNone(vals["partner_id"])
        assert vals["partner_name"] == self.partner_name

    def test_partner_not_found(self):
        self.partner.email = "different.email@example.com"
        vals = self.provider._map_stripe_transaction(self.transaction)
        self.assertIsNone(vals["partner_id"])

    def test_obtain_statement_data(self):
        with self._mock_balance_transaction_list(), self._mock_balance(3000):
            lines, statement_values = self.provider._obtain_statement_data(
                self.datetime_from, self.datetime_to
            )

        assert len(lines) == 2
        assert lines[0]["amount"] == 10
        assert lines[1]["amount"] == -0.40

        assert statement_values["balance_start"] == 30 - 10 + 0.40
        assert statement_values["balance_end_real"] == 30

    def test_api_key_not_defined(self):
        self.provider.stripe_api_key = None
        with pytest.raises(ValidationError):
            self.provider._obtain_statement_data(self.datetime_from, self.datetime_to)

    def test_bank_statement_lines_creation(self):
        with self._mock_balance_transaction_list(), self._mock_balance(0):
            self.provider._pull(self.datetime_from, self.datetime_to)

        lines = self._find_statement_lines()
        assert len(lines) == 2

    def test_bank_statement_lines__not_imported_twice(self):
        with self._mock_balance_transaction_list(), self._mock_balance(0):
            self.provider._pull(self.datetime_from, self.datetime_to)
            self.provider._pull(self.datetime_from, self.datetime_to)

        lines = self._find_statement_lines()
        assert len(lines) == 2

    def test_bank_statement_lines__no_fee(self):
        self.transaction["fee"] = 0

        with self._mock_balance_transaction_list(), self._mock_balance(0):
            self.provider._pull(self.datetime_from, self.datetime_to)

        lines = self._find_statement_lines()
        assert len(lines) == 1

    def _find_statement_lines(self):
        return self.env["account.bank.statement.line"].search(
            [
                ("stripe_id", "=", self.transaction_id),
            ]
        )

    @contextmanager
    def _mock_balance_transaction_list(self):
        def side_effect(created, **kwargs):
            return {
                "has_more": False,
                "data": self._get_filtered_transactions(created),
            }

        with patch("stripe.BalanceTransaction.list", side_effect=side_effect):
            yield

    def _get_filtered_transactions(self, created):
        transactions = self.transactions

        gte = created.get("gte")
        if gte:
            transactions = [t for t in transactions if gte <= t["created"]]
        lt = created.get("lt")
        if lt:
            transactions = [t for t in transactions if t["created"] < lt]

        return transactions

    @contextmanager
    def _mock_balance(self, amount):
        return_value = {
            "object": "balance",
            "pending": [
                {
                    "amount": amount,
                    "currency": "cad",
                }
            ],
        }

        with patch("stripe.Balance.retrieve", return_value=return_value):
            yield
