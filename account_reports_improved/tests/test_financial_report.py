# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestFinancialReport(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFinancialReport, cls).setUpClass()

        cls.report = cls.env['account.financial.html.report'].create({
            'name': 'Profit and Loss',
            'report_type': 'date_range',
        })

        cls.journal = cls.env['account.journal'].create({
            'company_id': cls.env.user.company_id.id,
            'code': 'TEST',
            'name': 'Test Journal',
            'type': 'general',
        })

        cls.income_type = cls.env['account.account.type'].create({
            'name': 'Income',
            'type': 'other',
        })

        cls.expense_type = cls.env['account.account.type'].create({
            'name': 'Expense',
            'type': 'other',
        })

        cls.asset_type = cls.env['account.account.type'].create({
            'name': 'Assets',
            'type': 'other',
            'include_initial_balance': True,
        })

        cls.income = cls.env['account.account'].create({
            'user_type_id': cls.income_type.id,
            'name': 'Revenus',
            'code': '400001 - test',
        })

        cls.expense = cls.env['account.account'].create({
            'user_type_id': cls.expense_type.id,
            'name': 'Expenses',
            'code': '500001 - test',
        })

        cls.asset = cls.env['account.account'].create({
            'user_type_id': cls.asset_type.id,
            'name': 'Assets',
            'code': '100001 - test',
        })

        cls.line_profit = (
            cls.env['account.financial.html.report.line'].create({
                'name': 'PROFIT',
                'code': 'PRO_TEST',
                'financial_report_id': cls.report.id,
                'formula_type': 'sum_of_children',
                'level': 0,
            }))

        cls.line_income = (
            cls.env['account.financial.html.report.line'].create({
                'name': 'Income',
                'code': 'INC_TEST',
                'formula_type': 'sum_of_categories',
                'account_type_ids': [(4, cls.income_type.id)],
                'reverse_sum': True,
                'level': 1,
                'parent_id': cls.line_profit.id,
            }))

        cls.line_expense = (
            cls.env['account.financial.html.report.line'].create({
                'name': 'Expenses',
                'code': 'EXP_TEST',
                'formula_type': 'sum_of_categories',
                'account_type_ids': [(4, cls.expense_type.id)],
                'reverse_sum': True,
                'level': 1,
                'parent_id': cls.line_profit.id,
            }))

        cls.create_move(cls.asset, cls.income, 100)
        cls.create_move(cls.expense, cls.asset, 200)

        cls.report_context = (
            cls.env['account.financial.html.report.context'].create({
                'report_id': cls.report.id,
            }))

    @classmethod
    def create_move(cls, debit_account, credit_account, amount):
        move = cls.env['account.move'].create({
            'name': '/',
            'journal_id': cls.journal.id,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'account_id': debit_account.id,
                    'debit': amount,
                }),
                (0, 0, {
                    'name': '/',
                    'account_id': credit_account.id,
                    'credit': amount,
                }),
            ]
        })

        move.post()

    def get_amount(self, report_line):
        res = {r['id']: r for r in self.report.with_context(
            no_format=True).get_lines(self.report_context)}
        return res[report_line.id]['columns'][0]

    def test_01_profit_amount(self):
        amount = self.get_amount(self.line_profit)
        self.assertEqual(amount, -100)

    def test_02_expense_amount(self):
        amount = self.get_amount(self.line_expense)
        self.assertEqual(amount, -200)

    def test_03_income_amount(self):
        amount = self.get_amount(self.line_income)
        self.assertEqual(amount, 100)

    def test_04_parent_updated_when_child_updated(self):
        self.line_income.write({
            'formula_type': 'sum_of_children', 'parent_id': False})
        old_parent_balance_before = self.line_profit.formulas
        new_parent_balance_before = self.line_income.formulas

        self.line_expense.write({'parent_id': self.line_income.id})
        old_parent_balance_after = self.line_profit.formulas
        new_parent_balance_after = self.line_income.formulas

        self.assertNotEqual(
            old_parent_balance_before, old_parent_balance_after)
        self.assertNotEqual(
            new_parent_balance_before, new_parent_balance_after)
