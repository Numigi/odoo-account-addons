# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _
from odoo.tests import common
from ..log_account_move_reversal import MOVE_REVERSAL_MESSAGE


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

    def test_message_logged_on_move_reversal(self):
        self.move.reverse_moves()
        message = self.move.message_ids.filtered(lambda m: _(MOVE_REVERSAL_MESSAGE) in m.body)
        assert len(message) == 1
