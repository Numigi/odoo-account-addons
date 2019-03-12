# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAccountMove(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test',
            'code': 'TEST',
            'type': 'general',
        })
        cls.analytic = cls.env['account.analytic.account'].create({'name': 'test'})
        cls.account_1 = cls.env['account.account'].create({
            'name': 'Account 1',
            'code': '501001',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
        })
        cls.account_2 = cls.env['account.account'].create({
            'name': 'Account 2',
            'code': '101001',
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
        cls.line_1 = cls.move.line_ids.filtered(lambda l: l.account_id == cls.account_1)
        cls.line_2 = cls.move.line_ids.filtered(lambda l: l.account_id == cls.account_2)

    def test_if_not_required_and_not_filled__no_constraint_raised(self):
        self.move.post()
        assert len(self.move.mapped('line_ids.analytic_line_ids')) == 0

    def test_if_not_forbidden_and_filled__no_constraint_raised(self):
        self.line_1.analytic_account_id = self.analytic
        self.line_2.analytic_account_id = self.analytic
        self.move.post()
        assert len(self.move.mapped('line_ids.analytic_line_ids')) == 2

    def test_if_required_and_not_filled__constraint_raised(self):
        self.account_1.analytic_account_required = True
        with pytest.raises(ValidationError):
            self.move.post()

    def test_if_forbidden_and_filled__constraint_raised(self):
        self.account_2.analytic_account_forbidden = True
        self.line_2.analytic_account_id = self.analytic
        with pytest.raises(ValidationError):
            self.move.post()
