# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestAccountMoveUniqueReversal(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test", "code": "TEST", "type": "general"}
        )
        cls.today = fields.date.today()
        cls.account_1 = cls.env["account.account"].create(
            {
                "name": "Account 1",
                "code": "501001",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.account_2 = cls.env["account.account"].create(
            {
                "name": "Account 2",
                "code": "101001",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_fixed_assets"
                ).id,
            }
        )
        cls.move = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "date": cls.today,
                "line_ids": [
                    (0, 0, {"account_id": cls.account_1.id, "name": "/", "debit": 75}),
                    (0, 0, {"account_id": cls.account_1.id, "name": "/", "debit": 25}),
                    (
                        0,
                        0,
                        {"account_id": cls.account_2.id, "name": "/", "credit": 100},
                    ),
                ],
            }
        )
        cls.move.action_post()

    def test_reverse_reversed_entry_fail(self):
        self._reverse_move(self.move)
        with self.assertRaises(UserError):
            self._reverse_move(self.move)

    def test_reverse_reversal_entry_fail(self):
        self._reverse_move(self.move)
        reversal_move = self.move.reversal_move_id
        with self.assertRaises(UserError):
            self._reverse_move(reversal_move)

    def _reverse_move(self, move):
        wizard_env = self.env["account.move.reversal"]
        wizard_env = wizard_env.with_context(active_ids=[move.id], active_model="account.move")
        wizard_env.create({"date": self.today}).reverse_moves()
