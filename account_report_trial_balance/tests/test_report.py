# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
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
        cls.report = cls.env["account.report.trial.balance"].create({
            "company_id": cls.company.id,
            "date_from": cls.date_from,
            "date_to": cls.date_to,
        })
        cls.journal = cls.env["account.journal"].create({
            "name": "My Journal",
            "code": "INV",
            "type": "general",
            "company_id": cls.company.id,
        })
        cls.account_1 = cls.env["account.account"].create({
            "company_id": cls.company.id,
            "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
            "name": "Receivable",
            "code": "10000",
            "reconcile": True,
        })
        cls.account_2 = cls.env["account.account"].create({
            "company_id": cls.company.id,
            "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            "name": "Payable",
            "code": "20000",
            "reconcile": True,
        })
        cls.account_3 = cls.env["account.account"].create({
            "company_id": cls.company.id,
            "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            "name": "Revenue",
            "code": "40000",
        })
        cls.account_4 = cls.env["account.account"].create({
            "company_id": cls.company.id,
            "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            "name": "Expense",
            "code": "50000",
        })
        cls.move_1 = cls._make_move(cls.account_1, cls.account_3, 300)
        cls.move_2 = cls._make_move(cls.account_4, cls.account_2, 200)

    @classmethod
    def _make_move(cls, debit_account, credit_account, amount):
        debit_vals = {
            "name": "/",
            "account_id": debit_account.id,
            "debit": amount,
            "company_id": cls.company.id,
        }
        credit_vals = {
            "name": "/",
            "account_id": credit_account.id,
            "credit": amount,
            "company_id": cls.company.id,
        }
        return cls.env["account.move"].create({
            "journal_id": cls.journal.id,
            "date": cls.date_from,
            "company_id": cls.company.id,
            "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
        })

    def test_one_line_per_account(self):
        lines = self._get_lines()
        assert len(lines) == 5
        assert lines[0]["account"] == self.account_1
        assert lines[1]["account"] == self.account_2
        assert lines[2]["account"] == self.account_3
        assert lines[3]["account"] == self.account_4

    def test_debit_credit_and_balance(self):
        self.move_1.post()
        self.move_2.post()

        lines = self._get_lines()
        assert lines[0]["debit"] == 300
        assert lines[0]["credit"] == 0
        assert lines[0]["balance"] == 300
        assert lines[1]["debit"] == 0
        assert lines[1]["credit"] == 200
        assert lines[1]["balance"] == -200
        assert lines[2]["debit"] == 0
        assert lines[2]["credit"] == 300
        assert lines[2]["balance"] == -300
        assert lines[3]["debit"] == 200
        assert lines[3]["credit"] == 0
        assert lines[3]["balance"] == 200

    def test_initial_and_closing_balance(self):
        self.move_1.date = self.date_from - timedelta(1)
        self.move_1.post()
        self.move_2.post()

        lines = self._get_lines()
        assert lines[0]["initial_balance"] == 300
        assert lines[1]["initial_balance"] == 0
        assert lines[2]["initial_balance"] == -300
        assert lines[3]["initial_balance"] == 0
        assert lines[0]["closing_balance"] == 300
        assert lines[1]["closing_balance"] == -200
        assert lines[2]["closing_balance"] == -300
        assert lines[3]["closing_balance"] == 200

    def test_initial_balance_clicked(self):
        res = self.report.initial_balance_clicked(self.account_1.id)
        assert res["domain"] == [
            ("account_id", "=", self.account_1.id),
            ("date", "<", self.date_from),
            ("move_id.state", "=", "posted"),
        ]

    def test_debit_clicked(self):
        res = self.report.debit_clicked(self.account_1.id)
        assert res["domain"] == self._get_period_domain(self.account_1)

    def test_credit_clicked(self):
        res = self.report.credit_clicked(self.account_1.id)
        assert res["domain"] == self._get_period_domain(self.account_1)

    def test_balance_clicked(self):
        res = self.report.balance_clicked(self.account_1.id)
        assert res["domain"] == self._get_period_domain(self.account_1)

    def _get_period_domain(self, account):
        return [
            ("account_id", "=", account.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("move_id.state", "=", "posted"),
        ]

    def test_closing_balance_clicked(self):
        res = self.report.closing_balance_clicked(self.account_1.id)
        assert res["domain"] == [
            ("account_id", "=", self.account_1.id),
            ("date", "<=", self.date_to),
            ("move_id.state", "=", "posted"),
        ]

    def _get_lines(self):
        return self.report.get_rendering_variables()["lines"]
