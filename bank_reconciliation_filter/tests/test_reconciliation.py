# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.tests import common


class TestReconciliation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bank_account = cls.env["account.account"].create(
            {
                "code": "11000",
                "name": "Bank Account",
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            }
        )
        cls.receivable_account = cls.env["account.account"].create(
            {
                "code": "12000",
                "name": "Receivable",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
            }
        )
        cls.payable_account = cls.env["account.account"].create(
            {
                "code": "22000",
                "name": "Payable",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )
        cls.expense_account = cls.env["account.account"].create(
            {
                "code": "55000",
                "name": "Expenses",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank US",
                "code": "BNK68",
                "type": "general",
                "default_credit_account_id": cls.bank_account.id,
                "default_debit_account_id": cls.bank_account.id,
            }
        )

        cls.partner = cls.env['res.partner'].create({'name': 'Supplier', 'supplier': True})
        cls.payment = cls._create_payment()
        cls.payment.post()
        cls.payment_bank_line = cls.payment.move_line_ids.filtered("credit")
        cls.payment_payable_line = cls.payment.move_line_ids.filtered("debit")

        cls.invoice_move = cls._create_invoice_move()
        cls.invoice_move.post()
        cls.invoice_payable_line = cls.invoice_move.line_ids.filtered("credit")

        cls.statement_line = cls._create_bank_statement_line()

    @classmethod
    def _create_payment(cls):
        return cls.env['account.payment'].create({
            'journal_id': cls.journal.id,
            'partner_id': cls.partner.id,
            'amount': 100,
            'payment_type': 'outbound',
            'payment_method_id': cls.env.ref('account.account_payment_method_manual_out').id,
            'partner_type': 'supplier',
        })

    @classmethod
    def _create_invoice_move(cls):
        invoice_debit_vals = {
            "account_id": cls.expense_account.id,
            "name": "/",
            "debit": 100,
            "partner_id": cls.partner.id,
        }

        invoice_credit_vals = {
            "account_id": cls.payable_account.id,
            "name": "/",
            "credit": 100,
            "partner_id": cls.partner.id,
        }

        return cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "date": datetime.now(),
                "line_ids": [(0, 0, invoice_debit_vals), (0, 0, invoice_credit_vals)],
            }
        )

    @classmethod
    def _create_bank_statement_line(cls):
        bank_stmt = cls.env["account.bank.statement"].create(
            {
                "journal_id": cls.journal.id,
                "date": datetime.now(),
                "name": "test",
            }
        )
        bank_stmt_line = cls.env["account.bank.statement.line"].create(
            {
                "name": "test",
                "statement_id": bank_stmt.id,
                "partner_id": cls.partner.id,
                "amount": -100,
                "date": datetime.now(),
            }
        )
        return bank_stmt_line

    def test_payment_bank_line_included(self):
        lines = self._get_move_lines()
        assert self.payment_bank_line in lines

    def test_payment_payable_line_excluded(self):
        lines = self._get_move_lines()
        assert self.payment_payable_line not in lines

    def test_invoice_payable_line_included(self):
        lines = self._get_move_lines()
        assert self.invoice_payable_line in lines

    def test_invoice_payable_line_excluded(self):
        self.journal.reconcile_show_payments_only = True
        lines = self._get_move_lines()
        assert self.invoice_payable_line not in lines

    def test_invoice_matching(self):
        aml_ids = self._apply_invoice_matching_rule()
        assert self.invoice_payable_line.id in aml_ids

    def test_invoice_matching__show_payments_only(self):
        self.journal.reconcile_show_payments_only = True
        aml_ids = self._apply_invoice_matching_rule()
        assert self.invoice_payable_line.id not in aml_ids

    def test_payment_matching(self):
        aml_ids = self._apply_invoice_matching_rule(exclude_payment=False)
        assert self.payment_bank_line.id in aml_ids

    def test_payment_matching__show_payments_only(self):
        self.journal.reconcile_show_payments_only = True
        aml_ids = self._apply_invoice_matching_rule(exclude_payment=False)
        assert self.payment_bank_line.id in aml_ids

    def _apply_invoice_matching_rule(self, exclude_payment=True):
        reconcile_model = self.env.ref("account.reconciliation_model_default_rule")
        excluded_ids = [self.payment_bank_line.id] if exclude_payment else []
        result = reconcile_model._apply_rules(self.statement_line, excluded_ids=excluded_ids)
        return result[self.statement_line.id]["aml_ids"]

    def _get_move_lines(self):
        widget = self.env["account.reconciliation.widget"]
        domain = widget._domain_move_lines_for_reconciliation(
            self.statement_line, [self.bank_account.id], self.partner.id,
        )
        return self.env["account.move.line"].search(domain)
