# Copyright 2021 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests import common


class TestReport(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "My Company"})
        cls.today = datetime.now().date()
        cls.date_from = cls.today - timedelta(30)
        cls.date_to = cls.today - timedelta(1)
        cls.report = cls.env["mis.report"].create({
            "name": "Income Statement",
            "description": "/",
        })
        cls.instance = cls.env["mis.report.instance"].create({
            "name": "2021",
            "report_id": cls.report.id,
            "period_ids": [(0, 0, {
                "name": "January",
            })]
        })

    def test_checkbox_not_checked(self):
        domain = self.instance.period_ids._get_additional_move_line_filter()
        assert ("is_closing", "=", False) not in domain

    def test_checkbox_checked(self):
        self.report.exclude_closing_entries = True
        domain = self.instance.period_ids._get_additional_move_line_filter()
        assert ("is_closing", "=", False) in domain
