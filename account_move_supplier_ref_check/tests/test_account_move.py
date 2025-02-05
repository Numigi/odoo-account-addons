# Copyright 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountMove(TransactionCase):

    def setUp(self):
        super(TestAccountMove, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Vendor',
        })
        self.product = self.env.ref("product.product_delivery_02")
        self.company = self.env.company

    def test_duplicate_supplier_reference(self):
        """Ensure that duplicate vendor bills are detected and raise an error."""

        invoice1 = self.env['account.move'].create({
            'move_type': "in_invoice",
            'ref': 'INV-2025-001',
            'partner_id': self.partner.id,
            'invoice_date': '2019-01-21',
            'date': '2019-01-21',
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1.0,
                    'name': 'product test 1',
                    'price_unit': 13.3,
                })
            ]
        })
        invoice1.action_post()

        invoice2 = self.env['account.move'].create({
            'move_type': "in_invoice",
            'ref': 'INV-2025-001',
            'partner_id': self.partner.id,
            'invoice_date': '2019-01-21',
            'date': '2019-01-21',
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1.0,
                    'name': 'product test 1',
                    'price_unit': 13.3,
                })
            ]
        })
        with self.assertRaises(ValidationError):
            invoice2.action_post()
