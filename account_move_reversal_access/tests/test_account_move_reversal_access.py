# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ddt import data, ddt, unpack

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
        cls.user_with_group_reverse_account_moves = cls.env["res.users"].create(
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
        cls.user_without_group_reverse_account_moves = cls.env["res.users"].create(
            {
                "name": "no_group",
                "login": "no_group",
                "email": "test_no_group@test.com",
                "groups_id": [(4, group_account_finance_billing.id)],
            }
        )

    @data(
        # reversal
        ("move_is_reversal", "journal_general", True),
        # auto_reverse
        ("move_is_auto_reverse", "journal_general", True),
        # normal
        ("move_normal", "journal_general", True),
        ("move_normal", "journal_bank", True),
        ("move_normal", "journal_cash", True),
        ("move_normal", "journal_general", False),
        ("move_normal", "journal_bank", False),
        ("move_normal", "journal_cash", False),
    )
    @unpack
    def test_can_post(self, move_type, journal_type, has_group):
        if has_group:
            user = self.user_with_group_reverse_account_moves
        else:
            user = self.user_without_group_reverse_account_moves
        move = self._create_move(move_type, journal_type, user)
        self._post_move_with_user(move, user)

    @data(
        ("move_is_reversal", "journal_bank", True),
        ("move_is_reversal", "journal_cash", True),
        ("move_is_reversal", "journal_general", False),
        ("move_is_reversal", "journal_bank", False),
        ("move_is_reversal", "journal_cash", False),
    )
    @unpack
    def test_cannot_create_reversal_move(self, move_type, journal_type, has_group):
        if has_group:
            user = self.user_with_group_reverse_account_moves
        else:
            user = self.user_without_group_reverse_account_moves
        with self.assertRaises(ValidationError):
            self._create_move(move_type, journal_type, user)

    @data(
        ("move_is_auto_reverse", "journal_bank", True),
        ("move_is_auto_reverse", "journal_cash", True),
        ("move_is_auto_reverse", "journal_general", False),
        ("move_is_auto_reverse", "journal_bank", False),
        ("move_is_auto_reverse", "journal_cash", False),
    )
    @unpack
    def test_cannot_post_auto_reverse_move(self, move_type, journal_type, has_group):
        if has_group:
            user = self.user_with_group_reverse_account_moves
        else:
            user = self.user_without_group_reverse_account_moves
        move = self._create_move(move_type, journal_type, user)
        with self.assertRaises(ValidationError):
            self._post_move_with_user(move, user)

    def _create_move(self, move_type, journal_type, user):
        if move_type == "move_is_reversal":
            create_move = self.__create_reversal_move
        elif move_type == "move_is_auto_reverse":
            create_move = self.__create_auto_reverse_move
        else:  # move_type == "move_normal"
            create_move = self.__create_normal_move
        move = create_move(journal_type, user)
        return move

    def __create_reversal_move(self, journal, user):
        move = self.__create_move(journal=journal, is_auto_reverse=False, user=user)
        today = fields.date.today()
        move.reverse_moves(today, False)
        reversal_move = move.reverse_entry_id
        return reversal_move

    def __create_auto_reverse_move(self, journal, user):
        move = self.__create_move(journal=journal, is_auto_reverse=True, user=user)
        return move

    def __create_normal_move(self, journal, user):
        move = self.__create_move(journal=journal, is_auto_reverse=False, user=user)
        return move

    def __create_move(self, journal, is_auto_reverse, user):
        journal = getattr(self, journal)
        return (
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

    @staticmethod
    def _post_move_with_user(move, user):
        move.sudo(user).post()
