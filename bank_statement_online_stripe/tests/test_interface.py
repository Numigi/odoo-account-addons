# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from contextlib import contextmanager
from datetime import datetime, timedelta
from odoo.tests import common
from unittest.mock import patch
from ..interface import BalanceTransactionInterface


class TestStripeTransactionInterface(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.api_key = "myapikey"
        self.datetime_from = datetime.now() - timedelta(30)
        self.datetime_to = self.datetime_from - timedelta(15)
        self.interface = BalanceTransactionInterface(
            api_key=self.api_key,
            datetime_from=self.datetime_from,
            datetime_to=self.datetime_to,
            currency="cad",
        )

        self.t1 = {
            "id": "txn_1",
            "object": "balance_transaction",
            "amount": 1000,
            "status": "available",
        }

        self.t2 = {
            "id": "txn_2",
            "object": "balance_transaction",
            "amount": 2000,
            "status": "available",
        }

        self.t3 = {
            "id": "txn_2",
            "object": "balance_transaction",
            "amount": 3000,
            "status": "available",
        }

        self.balance = 10000

        self.transactions = [
            self.t1,
            self.t2,
            self.t3,
        ]

    def test_list_transactions(self):
        with self._mock_balance_transaction_list():
            transactions = self.interface.list_transactions()

        assert transactions == self.transactions

    def test_test_start_balance(self):
        with self._mock_balance_transaction_list(), self._mock_balance():
            balance = self.interface.get_start_balance()

        assert balance == 100 - 10 - 20 - 30

    def test_test_end_balance(self):
        with self._mock_balance_transaction_list(), self._mock_balance():
            balance = self.interface.get_end_balance()

        assert balance == 100 - 10 - 20 - 30

    @contextmanager
    def _mock_balance_transaction_list(self):
        side_effect = [
            {"has_more": True, "data": [self.t1, self.t2]},
            {"has_more": False, "data": [self.t3]},
        ]
        with patch("stripe.BalanceTransaction.list", side_effect=side_effect):
            yield

    @contextmanager
    def _mock_balance(self):
        return_value = {
            "object": "balance",
            "pending": [
                {
                    "amount": self.balance,
                    "currency": "cad",
                }
            ],
        }
        with patch("stripe.Balance.retrieve", return_value=return_value):
            yield
