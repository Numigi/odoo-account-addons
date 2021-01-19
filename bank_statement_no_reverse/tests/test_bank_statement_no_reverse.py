# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.exceptions import UserError
from odoo.tests import common


@common.post_install(True)
class TestAccountMoveUniqueReversal(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_usd_id = cls.env.ref("base.USD").id
        cls.bank_journal_usd = cls.env["account.journal"].create(
            {
                "name": "Bank US",
                "type": "bank",
                "code": "BNK68",
                "currency_id": cls.currency_usd_id,
            }
        )
        cls.type_liquidity = cls.env.ref("account.data_account_type_liquidity")
        cls.type_receive = cls.env.ref("account.data_account_type_receivable")
        cls.type_pay = cls.env.ref("account.data_account_type_payable")
        cls.account_bank = cls.env["account.account"].create(
            {
                "code": "bank and cash usd",
                "name": "bank usd",
                "user_type_id": cls.type_liquidity.id,
            }
        )
        cls.account_rcv = cls.env["account.account"].create(
            {
                "code": "receive usd",
                "name": "receive usd",
                "reconcile": True,
                "user_type_id": cls.type_receive.id,
            }
        )
        cls.account_pay = cls.env["account.account"].create(
            {
                "code": "pay usd",
                "name": "pay usd",
                "reconcile": True,
                "user_type_id": cls.type_pay.id,
            }
        )
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.property_account_receivable_id = cls.account_rcv
        cls.partner.property_account_payable_id = cls.account_pay
        company = cls.env.ref("base.main_company")
        cls.expense_account = cls.env["account.account"].create(
            {
                "name": "EXP",
                "code": "EXP",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "company_id": company.id,
            }
        )

    def test_reconcile_bank_statement_line_with_new_entry_pass(self):
        payment = self._create_payment()
        move_line = self._get_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement()
        self._reconcile_bank_statement_line_with_move_line(
            bank_statement, move_line=move_line
        )

    def test_reconcile_bank_statement_line_with_reversed_entry_fail(self):
        payment = self._create_payment()
        self._revert_payment_entry(payment)
        move_line = self._get_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement()
        with self.assertRaises(UserError):
            self._reconcile_bank_statement_line_with_move_line(
                bank_statement, move_line=move_line
            )

    def test_reconcile_bank_statement_line_with_reversal_entry_fail(self):
        payment = self._create_payment()
        self._revert_payment_entry(payment)
        self._unreconcile_all_related_payment_journal_items(payment)
        reversal_move_line = self._get_reversal_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement()
        with self.assertRaises(UserError):
            self._reconcile_bank_statement_line_with_move_line(
                bank_statement,
                counterpart_aml_dicts=[
                    {
                        "name": "test",
                        "debit": 0,
                        "credit": 400,
                        "analytic_tag_ids": [[6, None, []]],
                        "move_line": reversal_move_line,
                    }
                ],
            )

    def test_reconcile_bank_statement_line_with_new_entry_partial_pass(self):
        payment = self._create_payment()
        move_line = self._get_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement(partial=True)
        self._reconcile_bank_statement_line_with_move_line(
            bank_statement, move_line=move_line
        )

    def test_reconcile_bank_statement_line_with_reversed_entry_partial_fail(self):
        payment = self._create_payment()
        self._revert_payment_entry(payment)
        move_line = self._get_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement(partial=True)
        with self.assertRaises(UserError):
            self._reconcile_bank_statement_line_with_move_line(
                bank_statement, move_line=move_line
            )

    def test_reconcile_bank_statement_line_with_reversal_entry_partial_fail(self):
        payment = self._create_payment()
        self._revert_payment_entry(payment)
        self._unreconcile_all_related_payment_journal_items(payment)
        reversal_move_line = self._get_reversal_move_line_from_payment(payment)
        bank_statement = self._create_bank_statement(partial=True)
        with self.assertRaises(UserError):
            self._reconcile_bank_statement_line_with_move_line(
                bank_statement,
                counterpart_aml_dicts=[
                    {
                        "name": "test",
                        "debit": 0,
                        "credit": 400,
                        "analytic_tag_ids": [[6, None, []]],
                        "move_line": reversal_move_line,
                    }
                ],
            )

    def _create_payment(self):
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "amount": 400,
                "currency_id": self.currency_usd_id,
                "payment_date": time.strftime("%Y") + "-07-15",
                "journal_id": self.bank_journal_usd.id,
            }
        )
        payment.post()
        return payment

    def _get_move_line_from_payment(self, payment):
        move_line = payment.move_line_ids.filtered(
            lambda r: r.account_id.user_type_id == self.type_liquidity
        )
        move_line.ensure_one()
        return move_line

    def _get_reversal_move_line_from_payment(self, payment):
        reversal_receive_move_line = payment.move_line_ids.mapped(
            "move_id"
        ).reverse_entry_id.line_ids.filtered(
            lambda r: r.account_id.user_type_id == self.type_receive
        )
        return reversal_receive_move_line

    def _create_bank_statement(self, partial=False):
        bank_stmt = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal_usd.id,
                "date": time.strftime("%Y") + "-07-15",
                "name": "test",
            }
        )
        amount = partial and 300 or 400
        bank_stmt_line = self.env["account.bank.statement.line"].create(
            {
                "name": "test",
                "statement_id": bank_stmt.id,
                "partner_id": self.partner.id,
                "amount": amount,
                "amount_currency": amount,
                "date": time.strftime("%Y") + "-07-15",
            }
        )
        return bank_stmt_line

    @staticmethod
    def _reconcile_bank_statement_line_with_move_line(
        bank_stmt_line, move_line=None, counterpart_aml_dicts=None
    ):
        bank_stmt_line.process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts, payment_aml_rec=move_line
        )

    @staticmethod
    def _revert_payment_entry(payment):
        payment.move_line_ids.mapped("move_id").reverse_moves()

    @staticmethod
    def _unreconcile_all_related_payment_journal_items(payment):
        (
            payment.move_line_ids
            + payment.move_line_ids.mapped("move_id").reverse_entry_id.line_ids
        ).remove_move_reconcile()
