# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests import common


class TestAccountMoveLine(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {
                "company_id": cls.env.user.company_id.id,
                "code": "TEST",
                "name": "Test Journal",
                "type": "general",
            }
        )

        cls.expense_type = cls.env.ref("account.data_account_type_expenses")
        cls.asset_type = cls.env.ref("account.data_account_type_current_assets")

        cls.expense = cls.env["account.account"].create(
            {
                "user_type_id": cls.expense_type.id,
                "name": "Revenus",
                "code": "400001 - test",
            }
        )

        cls.asset = cls.env["account.account"].create(
            {
                "user_type_id": cls.asset_type.id,
                "name": "Assets",
                "code": "100001 - test",
            }
        )

    def _get_expense_line(self, move):
        return move.line_ids.filtered(lambda l: l.account_id == self.expense)

    def _get_asset_line(self, move):
        return move.line_ids.filtered(lambda l: l.account_id == self.asset)

    def test_negative_debit(self):
        move = self._create_move([
            (0, 0, {"account_id": self.expense.id, "debit": -10,}),
            (0, 0, {"account_id": self.asset.id, "debit": 10,}),
        ])

        line = move.line_ids[0]
        assert line.debit == 0
        assert line.credit == 10

    def test_negative_credit(self):
        move = self._create_move([
            (0, 0, {"account_id": self.expense.id, "credit": 10,}),
            (0, 0, {"account_id": self.asset.id, "credit": -10,}),
        ])

        line = move.line_ids[1]
        assert line.debit == 10
        assert line.credit == 0

    def test_negative_debit_and_credit(self):
        move = self._create_move([
            (0, 0, {"account_id": self.expense.id, "credit": 10,}),
            (0, 0, {"account_id": self.asset.id, "credit": -10,}),
        ])

        expense_line = move.line_ids[0]
        assert expense_line.debit == 0
        assert expense_line.credit == 10

        asset_line = move.line_ids[1]
        assert asset_line.debit == 10
        assert asset_line.credit == 0

    def test_write(self):
        move = self._create_move([
            (0, 0, {"account_id": self.expense.id, "debit": 10,}),
            (0, 0, {"account_id": self.asset.id, "credit": 10,}),
        ])
        move.write(
            {
                "line_ids": [
                    (1, move.line_ids[0].id, {"debit": -10, "credit": 0}),
                    (1, move.line_ids[1].id, {"debit": 0, "credit": -10}),
                ]
            }
        )
        assert move.line_ids[0].credit == 10
        assert move.line_ids[1].debit == 10

    def _create_move(self, line_vals):
        return self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "date": datetime.now(),
                "line_ids": line_vals,
            }
        )
