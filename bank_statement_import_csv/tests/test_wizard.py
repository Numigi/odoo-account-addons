# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import date
from odoo.tests import common
from odoo.exceptions import ValidationError
from .common import get_file_base64


class TestWizard(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.cad = cls.env.ref("base.CAD")
        cls.usd = cls.env.ref("base.USD")

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank",
                "code": "BNK1",
                "type": "bank",
                "currency_id": cls.cad.id,
            }
        )

        cls.config = cls.env["bank.statement.import.config"].create(
            {
                "name": "Test",
                "date_format": "%Y-%m-%d",
                "first_row": 3,
                "delimiter": ",",
                "encoding": "cp1250",
                "reversed_order": True,
            }
        )

        cls.wizard = cls.env["bank.statement.import.wizard"].create(
            {
                "journal_id": cls.journal.id,
                "config_id": cls.config.id,
            }
        )

    def test_multi_currency(self):
        self._load_multi_currency_file()
        rows = self.wizard.line_ids
        assert len(rows) == 4

        row = rows[1]
        assert row["date"] == "2021-08-01"
        assert row["reference"] == "Z852755314"
        assert row["description"] == "quis nostrud exercitation ullamco"
        assert row["amount"] == "-149.40"
        assert row["currency_amount"] == "-116.71"
        assert row["currency"] == "USD"

    def test_mono_currency(self):
        self._load_mono_currency_file()
        assert len(self.wizard.line_ids) == 6
        assert self.wizard.show_confirm

    def test_wrong_date_format(self):
        self.config.date_index = 0
        self.config.date_format = "%Y-%m-%d"

        self.wizard.file = get_file_base64("cad_mono_currency.csv")
        self.wizard.load_file()
        rows = self.wizard.line_ids

        assert self.wizard.has_error
        assert not self.wizard.show_confirm
        assert rows[0].has_error

    def test_show_description(self):
        self.config.description_enabled = True
        assert self.wizard.show_description

    def test_show_reference(self):
        self.config.reference_enabled = True
        assert self.wizard.show_reference

    def test_show_balance(self):
        self.config.balance_enabled = True
        assert self.wizard.show_balance

    def test_show_currency_amount(self):
        self.config.currency_amount_enabled = True
        assert self.wizard.show_currency_amount

    def test_bank_statement__mono_currency(self):
        self._load_mono_currency_file()
        self.wizard.confirm()
        statement = self.wizard.statement_id
        lines = statement.line_ids
        assert len(lines) == 6

        assert lines[0].date == date(2021, 6, 18)
        assert lines[0].amount == 1138.24
        assert lines[1].amount == 4296.80
        assert lines[2].amount == 18396.00
        assert lines[3].amount == 0
        assert lines[4].amount == -183.30
        assert lines[5].amount == -1235.98

        assert statement.balance_start == 10730.38 - 1138.24
        assert statement.balance_end_real == 34475.86

    def test_bank_statement__multi_currency(self):
        self._load_multi_currency_file()
        self.wizard.confirm()
        statement = self.wizard.statement_id
        lines = statement.line_ids
        assert len(lines) == 4

        assert lines[0].date == date(2021, 8, 1)

        assert lines[0].amount == -456.25
        assert not lines[0].currency_id
        assert not lines[0].amount_currency

        assert lines[1].amount == -215.78
        assert not lines[1].currency_id
        assert not lines[1].amount_currency

        assert lines[2].amount == -149.40
        assert lines[2].currency_id == self.usd
        assert lines[2].amount_currency == -116.71

    def test_inactive_currency(self):
        self._load_multi_currency_file()
        self.usd.active = False
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def _add_wizard_line(self, **kwargs):
        self.wizard.write({"line_ids": [(0, 0, kwargs)]})

    def _load_mono_currency_file(self):
        self._setup_mono_currency_config()
        self.wizard.file = get_file_base64("cad_mono_currency.csv")
        self.wizard.load_file()

    def _load_multi_currency_file(self):
        self._setup_multi_currency_config()
        self.wizard.file = get_file_base64("cad_multi_currency.csv")
        self.wizard.load_file()

    def _setup_multi_currency_config(self):
        self.config.date_index = 0
        self.config.date_format = "%d/%m/%Y"
        self.config.description_enabled = True
        self.config.description_index = 3
        self.config.reference_enabled = True
        self.config.reference_index = 1
        self.config.withdraw_deposit_enabled = False
        self.config.amount_index = 4
        self.config.balance_enabled = False
        self.config.currency_amount_enabled = True
        self.config.currency_index = 5
        self.config.currency_amount_index = 6

    def _setup_mono_currency_config(self):
        self.config.date_index = 0
        self.config.date_format = "%d-%m-%Y"
        self.config.description_enabled = True
        self.config.description_index = 1
        self.config.reference_enabled = True
        self.config.reference_index = 2
        self.config.withdraw_deposit_enabled = True
        self.config.withdraw_index = 3
        self.config.deposit_index = 4
        self.config.balance_enabled = True
        self.config.balance_index = 5
        self.config.currency_amount_enabled = False
