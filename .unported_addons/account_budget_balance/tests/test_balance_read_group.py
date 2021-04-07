# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests import common


class TestBalanceReadGroup(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.budget_1 = cls.env['crossovered.budget'].create({
            'name': 'Budget Test 1',
            'date_from': datetime.now(),
            'date_to': datetime.now() + timedelta(365),
        })

        cls.budget_2 = cls.env['crossovered.budget'].create({
            'name': 'Budget Test 2',
            'date_from': datetime.now(),
            'date_to': datetime.now() + timedelta(365),
        })

        cls.account_1 = cls.env['account.analytic.account'].create({'name': 'Account 1'})
        cls.account_2 = cls.env['account.analytic.account'].create({'name': 'Account 2'})
        cls.account_3 = cls.env['account.analytic.account'].create({'name': 'Account 3'})

        cls.budget_line_1 = cls.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': cls.budget_1.id,
            'analytic_account_id': cls.account_1.id,
            'planned_amount': 1000,
            'date_from': cls.budget_1.date_from,
            'date_to': cls.budget_1.date_to,
        })

        cls.budget_line_2 = cls.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': cls.budget_1.id,
            'analytic_account_id': cls.account_2.id,
            'planned_amount': 2000,
            'date_from': cls.budget_1.date_from,
            'date_to': cls.budget_1.date_to,
        })

        cls.budget_line_3 = cls.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': cls.budget_2.id,
            'analytic_account_id': cls.account_3.id,
            'planned_amount': 5000,
            'date_from': cls.budget_2.date_from,
            'date_to': cls.budget_2.date_to,
        })

        cls.line_1 = cls.env['account.analytic.line'].create({
            'account_id': cls.account_1.id,
            'name': '/',
            'amount': 100,
        })

        cls.line_2 = cls.env['account.analytic.line'].create({
            'account_id': cls.account_2.id,
            'name': '/',
            'amount': 200,
        })

        cls.line_3 = cls.env['account.analytic.line'].create({
            'account_id': cls.account_3.id,
            'name': '/',
            'amount': 500,
        })

        cls.budget_lines = cls.budget_line_1 | cls.budget_line_2 | cls.budget_line_3
        cls.search_domain = [('id', 'in', cls.budget_lines.ids)]

    def test_read_group_by_budget(self):
        result = self.env['crossovered.budget.lines'].read_group(
            self.search_domain, ['balance'], ['crossovered_budget_id'],
            orderby='crossovered_budget_id asc'
        )

        assert len(result) == 2
        assert result[0]['balance'] == 2700  # 1000 + 2000 - 100 - 200
        assert result[1]['balance'] == 4500  # 5000 - 500

    def test_read_group_by_analytic_account(self):
        result = self.env['crossovered.budget.lines'].read_group(
            self.search_domain, ['balance'], ['analytic_account_id'],
            orderby='analytic_account_id asc'
        )

        assert len(result) == 3
        assert result[0]['balance'] == 900  # 1000 - 100
        assert result[1]['balance'] == 1800  # 2000 - 200
        assert result[2]['balance'] == 4500  # 5000 - 500
