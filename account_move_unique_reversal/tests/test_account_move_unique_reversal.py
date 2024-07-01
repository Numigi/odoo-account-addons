# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
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
        cls.journal_sale = cls.env["account.journal"].create(
            {
                "name": "Test Sales Journal",
                "code": "tSAL",
                "type": "sale",
            }
        )
        cls.journal_purchase = cls.env["account.journal"].create(
            {
                "name": "Test Purchase Journal",
                "code": "tPO",
                "type": "purchase",
            }
        )
        cls.today = fields.date.today()
        cls.account_1 = cls.env["account.account"].create(
            {
                "name": "Account 1",
                "code": "501001",
                "account_type": "expense",
            }
        )
        cls.account_2 = cls.env["account.account"].create(
            {
                "name": "Account 2",
                "code": "101001",
                "account_type": "asset_fixed",
            }
        )
        cls.move = cls._create_invoice(cls.journal)
        cls.move.action_post()

        cls.move_sale = cls._create_invoice(cls.journal_sale)
        cls.move_sale.action_post()

        cls.move_purchase = cls._create_invoice(cls.journal_purchase)
        cls.move_purchase.action_post()

    @classmethod
    def _create_invoice(cls, journal):
        move = cls.env["account.move"].create(
            {
                "journal_id": journal.id,
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
        return move

    def test_reverse_reversed_entry_fail(self):
        self._reverse_move(self.move)
        with self.assertRaises(UserError):
            self._reverse_move(self.move)

    def test_reverse_reversed_entry_sale_pass(self):
        self._reverse_move(self.move_sale)
        assert self._reverse_move(self.move_sale)

    def test_reverse_reversed_entry_purchase_pass(self):
        self._reverse_move(self.move_purchase)
        assert self._reverse_move(self.move_purchase)

    def test_reverse_reversal_entry_fail(self):
        self._reverse_move(self.move)
        reversal_move = self.move.reversal_move_id
        with self.assertRaises(UserError):
            self._reverse_move(reversal_move)

    def test_reverse_reversal_entry_sale_pass(self):
        self._reverse_move(self.move_sale)
        reversal_move = self.move_sale.reversal_move_id
        assert self._reverse_move(reversal_move)

    def test_reverse_reversal_entry_purchase_pass(self):
        self._reverse_move(self.move_purchase)
        reversal_move = self.move_purchase.reversal_move_id
        assert self._reverse_move(reversal_move)

    def _reverse_move(self, move):
        wizard_env = self.env["account.move.reversal"]
        wizard_env = wizard_env.with_context(
            active_ids=[move.id], active_model="account.move"
        )
        return wizard_env.create({"date": self.today}).reverse_moves()
