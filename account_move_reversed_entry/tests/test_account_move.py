# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestAccountMove(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].search([], limit=1)
        cls.account_1 = cls.env["account.account"].create(
            {
                "name": "Account 1",
                "code": "501001",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.account_2 = cls.env["account.account"].create(
            {
                "name": "Account 2",
                "code": "101001",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.move = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "line_ids": [
                    (0, 0, {"account_id": cls.account_1.id, "name": "/", "debit": 100}),
                    (0, 0, {"account_id": cls.account_2.id, "name": "/", "credit": 100}),
                ],
            }
        )
        cls.today = fields.date.today()

    def test_reversed_entry(self):
        self.move.reverse_moves()
        reversal_entry = self.move.reverse_entry_id
        assert reversal_entry.reversed_entry_id == self.move
