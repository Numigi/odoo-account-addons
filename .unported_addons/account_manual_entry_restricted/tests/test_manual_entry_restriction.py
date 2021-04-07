# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestManualEntryRestriction(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_1 = cls.env['res.groups'].create({'name': 'Group 1'})
        cls.group_2 = cls.env['res.groups'].create({'name': 'Group 2'})
        cls.journal = cls.env['account.journal'].search([], limit=1)
        cls.account_1 = cls.env['account.account'].create({
            'name': 'Account 1',
            'code': '111111',
            'user_type_id': cls.env.ref('account.data_account_type_fixed_assets').id,
        })
        cls.account_2 = cls.env['account.account'].create({
            'name': 'Account 2',
            'code': '111112',
            'user_type_id': cls.env.ref('account.data_account_type_fixed_assets').id,
        })
        cls.move = cls.env['account.move'].create({
            'journal_id': cls.journal.id,
            'line_ids': [
                (0, 0, {
                    'account_id': cls.account_1.id,
                    'name': '/',
                    'debit': 100,
                }),
                (0, 0, {
                    'account_id': cls.account_2.id,
                    'name': '/',
                    'credit': 100,
                })
            ]
        })

    def test_if_no_restriction__constraint_not_raised(self):
        self.move.action_post()
        assert self.move.state == 'posted'

    def test_if_user_not_member_of_group__constraint_raised(self):
        self.account_1.manual_entry_group_ids = self.group_1
        with pytest.raises(ValidationError):
            self.move.action_post()

    def test_if_user_member_of_group__constraint_not_raised(self):
        self.env.user.groups_id = self.group_1
        self.account_1.manual_entry_group_ids = self.group_1
        self.move.action_post()
        assert self.move.state == 'posted'

    def test_if_multiple_groups__user_must_be_member_of_one_group(self):
        self.env.user.groups_id = self.group_1
        self.account_1.manual_entry_group_ids = self.group_1 | self.group_2
        self.move.action_post()
        assert self.move.state == 'posted'

    def test_if_post_called_directly__constraint_not_raised(self):
        """Test that automatic entries are not restricted."""
        self.account_1.manual_entry_group_ids = self.group_1
        self.move.post()
        assert self.move.state == 'posted'
