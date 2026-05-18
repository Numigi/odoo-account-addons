# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install")
class TestAccountMoveReversalAccess(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.general_journal = cls.company_data["default_journal_misc"]
        cls.journal_cash = cls.company_data["default_journal_cash"]
        cls.journal_bank = cls.company_data["default_journal_bank"]

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
        cls.journals = [
            cls.general_journal,
            cls.journal_bank,
            cls.journal_cash,
        ]

    def test_can_post_move_is_reversal_has_group(self):
        self.__create_reversal_move(self.general_journal, self.user_with_group)

    def test_can_post_move_normal_has_group(self):
        # Apply to "journal_general", "journal_bank" and "journal_cash"
        for journal_type in self.journals:
            self.__create_normal_move(journal_type, self.user_with_group)

    def test_can_post_move_normal_no_group(self):
        # Apply to "journal_general", "journal_bank" and "journal_cash"
        for journal_type in self.journals:
            self.__create_normal_move(journal_type, self.user_without_group)

    def test_cannot_post_move_is_reversal_has_group(self):
        # Apply only with "journal_bank" and "journal_cash"
        journals = self.journals[1:]
        for journal_type in journals:
            with self.assertRaises(ValidationError):
                self.__create_reversal_move(journal_type, self.user_with_group)

    def test_cannot_post_move_is_reversal_no_group(self):
        # Apply to "journal_general", "journal_bank" and "journal_cash"
        for journal_type in self.journals:
            with self.assertRaises(ValidationError):
                self.__create_reversal_move(journal_type, self.user_without_group)

    def __create_reversal_move(self, journal_type, user):
        move = self.__create_move(journal_type, user)
        today = fields.date.today()
        wizard = self.env["account.move.reversal"].with_context(
            active_ids=[move.id], active_model="account.move"
        )
        wizard.with_user(user).create(
            {"date": today, "journal_id": journal_type.id}
        ).with_user(user).reverse_moves()
        return move.reversal_move_id

    def __create_normal_move(self, journal_type, user):
        move = self.__create_move(journal_type, user)
        return move

    def __create_move(self, journal, user):
        move = (
            self.env["account.move"]
            .with_user(user)
            .create(
                {
                    "journal_id": journal.id,
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
        move._post()
        return move
