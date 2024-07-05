# Copyright 2019 Numigi and all its contributors (https://bit.ly/numigiens)
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestAccountMove(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test',
            'code': 'TEST',
            'type': 'general',
        })
        cls.default_plan = cls.env['account.analytic.plan'].create(
            {'name': 'Default', 'company_id': False})
        cls.analytic = cls.env['account.analytic.account'].create({
            'name': 'test',
            'plan_id': cls.default_plan.id
        })
        cls.account_1 = cls.env['account.account'].create({
            'name': 'Account 1',
            'code': '501001',
            'account_type': 'asset_fixed',
        })
        cls.account_2 = cls.env['account.account'].create({
            'name': 'Account 2',
            'code': '101001',
            'account_type': 'expense',
        })

        cls.today = datetime.now().date()
        cls.yesterday = cls.today - timedelta(1)

        cls.move = cls.env['account.move'].create({
            'journal_id': cls.journal.id,
            'date': cls.today,
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

    def test_if_reversed_prior_to_original_move__validation_raised(self):
        with pytest.raises(ValidationError):
            self._reverse_moves(date=self.yesterday)

    def test_if_reversed_with_same_date__reversal_move_created(self):
        assert self._reverse_moves(date=self.today)

    def _reverse_moves(self, date):
        return self.move._reverse_moves([{"date": date}])
