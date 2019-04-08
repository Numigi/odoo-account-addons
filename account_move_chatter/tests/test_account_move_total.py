# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


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
                    'debit': 75,
                }),
                (0, 0, {
                    'account_id': cls.account_1.id,
                    'name': '/',
                    'debit': 25,
                }),
                (0, 0, {
                    'account_id': cls.account_2.id,
                    'name': '/',
                    'credit': 100,
                })
            ]
        })

    def test_move_total_is_sum_of_debit(self):
        assert self.move.total_amount == 100

    def test_if_change_move_line_amount__total_is_updated(self):
        self.move.write({
            'line_ids': [
                (5, 0),
                (0, 0, {
                    'account_id': self.account_1.id,
                    'name': '/',
                    'debit': 200,
                }),
                (0, 0, {
                    'account_id': self.account_2.id,
                    'name': '/',
                    'credit': 200,
                })
            ]
        })
        assert self.move.total_amount == 200
