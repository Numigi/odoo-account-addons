# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime, timedelta
from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class TestWizard(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "My Company"})
        cls.today = datetime.now().date()
        cls.date_from = cls.today - timedelta(30)
        cls.date_to = cls.today - timedelta(1)

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Invoices",
                "code": "INV",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.closing_journal = cls.env["account.journal"].create(
            {
                "name": "Closing Journal",
                "code": "CLOSE",
                "type": "general",
                "company_id": cls.company.id,
                "is_closing": True,
            }
        )

        cls.earnings_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_equity").id,
                "name": "Retained Earnings",
                "code": "31000",
                "is_default_earnings_account": True,
            }
        )

        cls.receivable_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "name": "Receivable",
                "code": "10000",
                "reconcile": True,
            }
        )
        cls.payable_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "name": "Payable",
                "code": "20000",
                "reconcile": True,
            }
        )
        cls.revenue_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
                "name": "Revenue",
                "code": "40000",
            }
        )
        cls.expense_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "name": "Expense",
                "code": "50000",
            }
        )
        cls.move_1 = cls._make_move(
            cls.receivable_account, cls.revenue_account, 300)
        cls.move_2 = cls._make_move(
            cls.expense_account, cls.payable_account, 200)
        cls.move_1.company_id = cls.move_2.company_id = cls.company.id

        cls.wizard = cls.env["account.closing.wizard"].create(
            {
                "company_id": cls.company.id,
                "date_from": cls.date_from,
                "date_to": cls.date_to,
                "journal_id": cls.closing_journal.id,
            }
        )

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
        return cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "date": cls.date_from,
                "company_id": cls.company.id,
                "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
            }
        )

    def test_default_journal(self):
        self.env.user.company_id = self.company
        assert self.wizard._get_default_journal_id() == self.closing_journal

    def test_confirm__no_posted_entry(self):
        company_user = self.env.user.company_id
        self.env.user.write({
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id), (4, company_user.id)],
        })
        with pytest.raises(ValidationError):
            self.wizard.confirm()
        move = self.wizard.move_id
        assert move.date != self.date_to
        assert move.company_id != self.company
        assert move.journal_id != self.closing_journal
        assert move.state != "draft"
        assert move.is_closing is False

        lines = move.line_ids
        assert len(lines) == 0

    def test_confirm__entries_posted(self):
        self.move_1.action_post()
        self.move_2.action_post()

        self.wizard.confirm()
        move = self.wizard.move_id
        lines = move.line_ids
        assert len(lines) == 3
        assert lines[0].account_id == self.earnings_account
        assert lines[1].account_id == self.revenue_account
        assert lines[2].account_id == self.expense_account
        assert lines[0].credit == 100
        assert lines[1].debit == 300
        assert lines[2].credit == 200

    def test_account_move_ref(self):
        self.move_1.action_post()
        self.move_2.action_post()
        date_from = self.date_from.strftime(DATE_FORMAT)
        date_to = self.date_to.strftime(DATE_FORMAT)
        self.wizard.confirm()
        move = self.wizard.move_id
        assert date_from in move.ref
        assert date_to in move.ref

    def test_account_move_close_draft_in_period_multi_comp(self):
        company_user = self.env.user.company_id
        self.env.user.write({
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id), (4, company_user.id)],
        })
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def test_account_move_close_draft_in_period_multi_comp_raising_exception(self):
        company_user = self.env.user.company_id
        self.env.user.write({
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id), (4, company_user.id)],
        })
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def test_account_move_close_draft_in_period_no_exception_raised(self):
        self.wizard.confirm()

    def test_account_move_close_draft_in_period_no_record(self):
        domain = [("state", "=", "draft"), ("company_id", "=", self.env.user.company_id.id),
                  ("date", "<=", self.date_to)]
        account_ids = self.env["account.move"].search(domain)
        assert len(account_ids.ids) == 0

    def test_no_earnings_account(self):
        self.earnings_account.is_default_earnings_account = False
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def test_two_earnings_account(self):
        new_account = self.earnings_account.copy()
        with pytest.raises(ValidationError):
            new_account.is_default_earnings_account = True
