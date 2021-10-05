# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
from decimal import Decimal
from odoo.tests import common
from .common import open_file
from ..loader import BankStatementLoader


class TestMonoCurrencyCSV(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.config = {
            "first_row": 2,
            "date": {
                "index": 0,
                "format": "%d-%m-%Y",
            },
            "description": {
                "index": 1,
            },
            "reference": {
                "index": 2,
            },
            "withdraw": {
                "index": 3,
            },
            "deposit": {
                "index": 4,
            },
            "balance": {
                "index": 5,
            },
        }

    def test_number_of_rows(self):
        rows = self._get_rows()
        assert len(rows) == 6

    def test_date(self):
        rows = self._get_rows()
        assert rows[0]["date"] == "2021-07-05"

    def test_date_wrong_format(self):
        self.config["date"]["format"] = "%d/%m/%Y"
        rows = self._get_rows()
        assert rows[0]["error"]

    def test_amount_withdraw(self):
        rows = self._get_rows()
        assert rows[0]["amount"] == "-1235.98"

    def test_amount_deposit(self):
        rows = self._get_rows()
        assert rows[3]["amount"] == "18396.00"

    def test_balance(self):
        rows = self._get_rows()
        assert rows[0]["balance"] == "79082.64"

    def test_description(self):
        rows = self._get_rows()
        assert rows[0]["description"] == "Lorem ipsum"

    def test_reference(self):
        rows = self._get_rows()
        assert rows[0]["reference"] == "CPI080000000666"

    def test_index_exceeding_row(self):
        self.config["reference"]["index"] = 100
        rows = self._get_rows()
        assert rows[0]["reference"] == ""

    def _get_rows(self):
        with open_file("cad_mono_currency.csv") as file:
            data = self._get_loader().load(file)
            return data["rows"]

    def _get_loader(self):
        return BankStatementLoader(self.config)


class TestMultiCurrencyCSV(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.config = {
            "first_row": 2,
            "amount": {
                "index": 4,
            },
            "currency": {
                "index": 5,
            },
            "currency_amount": {
                "index": 6,
            },
        }

    def test_amount(self):
        rows = self._get_rows()
        assert rows[1]["amount"] == "-149.40"

    def test_currency(self):
        rows = self._get_rows()
        assert rows[1]["currency"] == "USD"

    def test_amount_currency(self):
        rows = self._get_rows()
        assert rows[1]["currency_amount"] == "-116.71"

    def _get_rows(self):
        loader = BankStatementLoader(self.config)

        with open_file("cad_multi_currency.csv") as file:
            data = loader.load(file)
            return data["rows"]
