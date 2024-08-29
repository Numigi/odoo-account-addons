# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestAccountMove(TransactionCase):

    def setUp(self):
        super(TestAccountMove, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
        })
        self.invoice = self.env['account.move'].create([
            {
                'move_type': 'out_invoice',
                'date': '2017-01-01',
                'invoice_date': '2017-01-01',
                'partner_id': self.partner.id,
                'invoice_line_ids': [
                    (0, 0, {'name': 'aaaa', 'price_unit': 100.0})
                ],
            }
        ])

    def test_invoice_without_date(self):
        self.invoice.invoice_date = False
        with self.assertRaises(UserError):
            self.invoice.action_post()

    def test_invoice_with_date(self):
        self.invoice.invoice_date = '2023-08-01'
        self.invoice.action_post()
        self.assertEqual(self.invoice.state, 'posted')
