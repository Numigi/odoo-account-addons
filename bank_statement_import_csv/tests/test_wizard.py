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
                "first_row": 2,
                "delimiter": ",",
                "encoding": "cp1250",
            }
        )

        cls.wizard = cls.env["bank.statement.import.wizard"].create(
            {
                "config_id": cls.config.id,
                "file": get_file_base64("cad_multi_currency.csv"),
            }
        )

    @classmethod
    def _get_file_base64_content(cls, file_name):
        file = open_file_base64(file_name, "rb")
        return base64.b64encode(file.read())

    def test_data(self):
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

        self.wizard.load_file()
        rows = self.wizard.data["rows"]
        assert len(rows) == 4

        row = rows[1]
        assert row["date"] == "2021-08-01"
        assert row["reference"] == "Z852755314"
        assert row["description"] == "quis nostrud exercitation ullamco"
        assert row["amount"] == "-149.40"
        assert row["currency_amount"] == "-116.71"
        assert row["currency"] == "USD"
