# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest

from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestAccountMoveUniqueReversal(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank US",
                "code": "BNK68",
                "type": "general",
            }
        )
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
        cls.amount = 100

        cls.statement_line = cls._create_bank_statement_line()

        debit_vals = {
            "account_id": cls.bank_account.id,
            "name": "/",
            "debit": cls.amount,
        }

        credit_vals = {
            "account_id": cls.receivable_account.id,
            "name": "/",
            "credit": cls.amount,
        }

        cls.move = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "date": datetime.now(),
                "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
            })

        cls.move.post()

        cls.move_line = cls.move.line_ids.filtered("credit")

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
                "amount": cls.amount,
                "date": datetime.now(),
            }
        )
        return bank_stmt_line

    def test_reconcile_line(self):
        self.move_line.statement_line_id = self.statement_line

    def test_reconcile_reversed_line(self):
        self.move.reverse_moves()
        with pytest.raises(ValidationError):
            self.move_line.statement_line_id = self.statement_line

    def test_reverse_move(self):
        self.move.reverse_moves()

    def test_reverse_move_reconciled_line(self):
        self.move_line.statement_line_id = self.statement_line
        with pytest.raises(ValidationError):
            self.move.reverse_moves()

    def test_reconcile_reversal_line(self):
        self.move.reverse_moves()
        reversal_line = self.move.reverse_entry_id.line_ids.filtered("debit")

        with pytest.raises(ValidationError):
            reversal_line.statement_line_id = self.statement_line
