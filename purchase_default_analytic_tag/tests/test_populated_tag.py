# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestPopulatedTag(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_tag1 = cls.env['account.analytic.tag'].create({
            'name': 'Tag 1',
        })
        cls.analytic_tag2 = cls.env['account.analytic.tag'].create({
            'name': 'Tag 2',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'analytic_tag_ids': [(6, 0, [cls.analytic_tag1.id, cls.analytic_tag2.id])]
        })

    def test_po_select_product_populate_tags(self):
        purchase_order_line = self.env["purchase.order.line"].new({
            "product_id": self.product.id,
        })
        purchase_order_line.onchange_product_id()
        self.assertTrue(
            self.analytic_tag1 in purchase_order_line.analytic_tag_ids
            and self.analytic_tag2 in purchase_order_line.analytic_tag_ids
        )

    def test_invoice_select_product_populate_tags(self):
        invoice_line = self.env["account.invoice.line"].new({
            "product_id": self.product.id,
        })
        invoice_line._onchange_product_id()
        self.assertTrue(
            self.analytic_tag1 in invoice_line.analytic_tag_ids
            and self.analytic_tag2 in invoice_line.analytic_tag_ids
        )
