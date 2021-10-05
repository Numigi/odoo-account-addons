# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
from datetime import datetime, timedelta, date
from odoo import fields
from odoo.tests import common
from .common import get_file_base64


class TestWizard(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.config = cls.env["bank.statement.import.config"].create(
            {
                "name": "Test",
                "first_row": 2,
                "delimiter": ",",
                "encoding": "cp1250",
            }
        )

        cls.wizard = cls.env["bank.statement.import.wizard"].create(
            {
                "config_id": cls.config.id,
            }
        )

    @classmethod
    def _get_file_base64_content(cls, file_name):
        file = open_file_base64(file_name, "rb")
        return base64.b64encode(file.read())

    def test_multi_currency(self):
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

        self.wizard.file =  get_file_base64("cad_multi_currency.csv")
        self.wizard.load_file()
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

        self.wizard.file =  get_file_base64("cad_mono_currency.csv")
        self.wizard.load_file()
        rows = self.wizard.line_ids
        assert len(rows) == 6

        row = rows[0]
        assert row["date"] == "2021-07-05"
        assert row["reference"] == "CPI080000000666"
        assert row["description"] == "Lorem ipsum"
        assert row["amount"] == "-1235.98"
        assert row["balance"] == "79082.64"
        assert rows[3]["amount"] == "18396.00"

        assert self.wizard.show_confirm        

    def test_wrong_date_format(self):
        self.config.date_index = 0
        self.config.date_format = "%Y-%m-%d"

        self.wizard.file =  get_file_base64("cad_mono_currency.csv")
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

    def _add_wizard_line(self, **kwargs):
        self.wizard.write({"line_ids": [(0, 0, kwargs)]})
