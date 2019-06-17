# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests import common


class TestGetMoveLineDomain(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date_from = datetime.now()
        cls.date_to = datetime.now() + timedelta(365)
        cls.budget_1 = cls.env['crossovered.budget'].create({
            'name': 'Budget Test 1',
            'date_from': cls.date_from,
            'date_to': cls.date_to,
        })

        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Analytic Account 1'
        })

        cls.account = cls.env['account.account'].create({
            'name': 'General Expenses',
            'code': '510100',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
        })

        cls.budget_position = cls.env['account.budget.post'].create({
            'name': 'General Expenses',
            'account_ids': [(4, cls.account.id)],
        })

        cls.budget_line_1 = cls.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': cls.budget_1.id,
            'analytic_account_id': cls.analytic_account.id,
            'general_budget_id': cls.budget_position.id,
            'planned_amount': 1000,
            'date_from': cls.budget_1.date_from,
            'date_to': cls.budget_1.date_to,
        })

    def _get_move_line_domain(self):
        return self.budget_line_1.action_view_move_lines()['domain']

    def test_move_date_between_budget_boundaries(self):
        domain = self._get_move_line_domain()
        assert ('date', '>=', self.budget_1.date_from) in domain
        assert ('date', '<=', self.budget_1.date_to) in domain

    def test_if_budget_line_has_budget_position__general_account_filtered(self):
        self.budget_line_1.general_budget_id = self.budget_position
        domain = self._get_move_line_domain()
        assert ('account_id', 'in', [self.account.id]) in domain

    def test_if_budget_line_has_analytic_account__analytic_account_filtered(self):
        self.budget_line_1.analytic_account_id = self.analytic_account
        domain = self._get_move_line_domain()
        assert ('analytic_account_id', '=', self.analytic_account.id) in domain
