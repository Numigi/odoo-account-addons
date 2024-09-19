# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import time

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestBankStatement(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        # Set the chart_template_ref to the generic COA if not provided
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]

        cls.bank_stmt1 = cls.acc_bank_stmt_model.create(
            {
                "name": "Statment 1",
                "company_id": cls.env.ref("base.main_company").id,
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
            }
        )

        cls.bank_stmt2 = cls.acc_bank_stmt_model.create(
            {
                "name": "Statment 2",
                "company_id": cls.env.ref("base.main_company").id,
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y-07-16"),
            }
        )

        cls.bank_stmt_line1 = cls.acc_bank_stmt_line_model.create(
            {
                "name": "Test Line  1",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": cls.bank_stmt1.id,
                "amount": 150,
                "date": time.strftime("%Y-07-15"),
            }
        )
        cls.bank_stmt_line2 = cls.acc_bank_stmt_line_model.create(
            {
                "name": "Test Line  2",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": cls.bank_stmt1.id,
                "amount": 50,
                "date": time.strftime("%Y-07-15"),
            }
        )

        cls.bank_stmt_line3 = cls.acc_bank_stmt_line_model.create(
            {
                "name": "Test Line  3",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": cls.bank_stmt2.id,
                "amount": 350,
                "date": time.strftime("%Y-07-15"),
            }
        )

    def test_not_confirm_statement_if_not_valid(self):
        self.bank_stmt1.balance_end_real = 200
        self.bank_stmt2.balance_start = 400
        with self.assertRaises(ValidationError):
            self.bank_stmt2.action_confirm_statement()

    def test_confirm_statement(self):
        self.bank_stmt1.balance_end_real = 200
        self.bank_stmt2.balance_start = 200
        inv1 = self.create_invoice(currency_id=self.currency_euro_id,
            invoice_amount=350)
        with Form(self.bank_stmt_line3,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view", ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable")
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
        self.assertTrue(self.bank_stmt_line3.can_reconcile)
        self.bank_stmt_line3.reconcile_bank_line()
        self.bank_stmt2.action_confirm_statement()
