# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests import common


class TestAccountMoveLine(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env['account.journal'].create({
            'company_id': cls.env.user.company_id.id,
            'code': 'TEST',
            'name': 'Test Journal',
            'type': 'general',
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

        cls.expense = cls.env['account.account'].create({
            'user_type_id': cls.expense_type.id,
            'name': 'Revenus',
            'code': '400001 - test',
        })

        cls.asset = cls.env['account.account'].create({
            'user_type_id': cls.asset_type.id,
            'name': 'Assets',
            'code': '100001 - test',
        })

    def _get_expense_line(self, move):
        return move.line_ids.filtered(lambda l: l.account_id == self.expense)

    def _get_asset_line(self, move):
        return move.line_ids.filtered(lambda l: l.account_id == self.asset)

    def test_negative_debit(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal.id,
            'date': datetime.now(),
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense.id,
                    'debit': -10,
                }),
                (0, 0, {
                    'account_id': self.asset.id,
                    'debit': 10,
                }),
            ]
        })

        line = self._get_expense_line(move)
        self.assertEqual(line.debit, 0)
        self.assertEqual(line.credit, 10)

    def test_negative_credit(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal.id,
            'date': datetime.now(),
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense.id,
                    'credit': -10,
                }),
                (0, 0, {
                    'account_id': self.asset.id,
                    'credit': 10,
                }),
            ]
        })

        line = self._get_expense_line(move)
        self.assertEqual(line.debit, 10)
        self.assertEqual(line.credit, 0)

    def test_negative_debit_and_credit(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal.id,
            'date': datetime.now(),
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense.id,
                    'debit': -10,
                }),
                (0, 0, {
                    'account_id': self.asset.id,
                    'credit': -10,
                }),
            ]
        })

        expense_line = self._get_expense_line(move)
        self.assertEqual(expense_line.debit, 0)
        self.assertEqual(expense_line.credit, 10)

        asset_line = self._get_asset_line(move)
        self.assertEqual(asset_line.debit, 10)
        self.assertEqual(asset_line.credit, 0)
