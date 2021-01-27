# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ddt import data, ddt

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


@ddt
class TestAccountMoveReversalAccess(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal_general = cls.env["account.journal"].create(
            {"name": "journal_general", "code": "journal_general", "type": "general"}
        )
        cls.journal_cash = cls.env["account.journal"].create(
            {"name": "journal_cash", "code": "journal_cash", "type": "cash"}
        )
        cls.journal_bank = cls.env["account.journal"].create(
            {"name": "journal_bank", "code": "journal_bank", "type": "bank"}
        )
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
        group_reverse_account_moves = cls.env.ref(
            "account_move_reversal_access.group_reverse_account_moves"
        )
        group_account_finance_billing = cls.env.ref("account.group_account_invoice")
        cls.user_with_group = cls.env["res.users"].create(
            {
                "name": "has_group",
                "login": "has_group",
                "email": "test_has_group@test.com",
                "groups_id": [
                    (4, group_reverse_account_moves.id),
                    (4, group_account_finance_billing.id),
                ],
            }
        )
        cls.user_without_group = cls.env["res.users"].create(
            {
                "name": "no_group",
                "login": "no_group",
                "email": "test_no_group@test.com",
                "groups_id": [(4, group_account_finance_billing.id)],
            }
        )

    @data("journal_general")
    def test_can_post_move_is_auto_reverse_has_group(self, journal_type):
        self.__create_auto_reverse_move(journal_type, self.user_with_group)

    @data("journal_general")
    def test_can_post_move_is_reversal_has_group(self, journal_type):
        self.__create_reversal_move(journal_type, self.user_with_group)

    @data("journal_general", "journal_bank", "journal_cash")
    def test_can_post_move_normal_has_group(self, journal_type):
        self.__create_normal_move(journal_type, self.user_with_group)

    @data("journal_general", "journal_bank", "journal_cash")
    def test_can_post_move_normal_no_group(self, journal_type):
        self.__create_normal_move(journal_type, self.user_without_group)

    @data("journal_bank", "journal_cash")
    def test_cannot_post_move_is_reversal_has_group(self, journal_type):
        with self.assertRaises(ValidationError):
            self.__create_reversal_move(journal_type, self.user_with_group)

    @data("journal_general", "journal_bank", "journal_cash")
    def test_cannot_post_move_is_reversal_no_group(self, journal_type):
        with self.assertRaises(ValidationError):
            self.__create_reversal_move(journal_type, self.user_without_group)

    @data("journal_bank", "journal_cash")
    def test_cannot_post_move_is_auto_reverse_has_group(self, journal_type):
        with self.assertRaises(ValidationError):
            self.__create_auto_reverse_move(journal_type, self.user_with_group)

    @data("journal_general", "journal_bank", "journal_cash")
    def test_cannot_post_move_is_auto_reverse_no_group(self, journal_type):
        with self.assertRaises(ValidationError):
            self.__create_auto_reverse_move(journal_type, self.user_without_group)

    def __create_reversal_move(self, journal_type, user):
        move = self.__create_move(journal_type, False, user)
        today = fields.date.today()
        wizard = self.env["account.move.reversal"].with_context(active_ids=[move.id])
        wizard.sudo(user).create({"date": today}).sudo(user).reverse_moves()
        reversal_move = move.reverse_entry_id
        return reversal_move

    def __create_auto_reverse_move(self, journal_type, user):
        move = self.__create_move(journal_type, True, user)
        return move

    def __create_normal_move(self, journal_type, user):
        move = self.__create_move(journal_type, False, user)
        return move

    def __create_move(self, journal_type, is_auto_reverse, user):
        journal = getattr(self, journal_type)
        move = (
            self.env["account.move"]
            .sudo(user)
            .create(
                {
                    "journal_id": journal.id,
                    "auto_reverse": is_auto_reverse,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_1.id,
                                "name": "/",
                                "debit": 75,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_1.id,
                                "name": "/",
                                "debit": 25,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_2.id,
                                "name": "/",
                                "credit": 100,
                            },
                        ),
                    ],
                }
            )
        )
        move.post()
        return move
