# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from . import common


class TestPurchaseOrder(common.TestSaleOrderBase):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'P. Lamarche inc.',
            'is_company': True,
        })

        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'My Project',
        })

        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.supplier.id,
        })

        cls.product_uom = cls.env.ref('product.product_uom_unit')

        cls.purchase_line_1 = cls.env['purchase.order.line'].create({
            'name': cls.product_1.name,
            'product_id': cls.product_1.id,
            'order_id': cls.purchase_order.id,
            'product_qty': 1,
            'price_unit': 500.00,
            'account_analytic_id': cls.analytic_account.id,
            'product_uom': cls.product_uom.id,
            'date_planned': cls.today,
        })

        cls.purchase_line_2 = cls.env['purchase.order.line'].create({
            'name': cls.product_2.name,
            'product_id': cls.product_2.id,
            'order_id': cls.purchase_order.id,
            'product_qty': 10,
            'price_unit': 30.00,
            'account_analytic_id': cls.analytic_account.id,
            'product_uom': cls.product_uom.id,
            'date_planned': cls.today,
        })

        cls.purchase_line_3 = cls.env['purchase.order.line'].create({
            'name': cls.product_2.name,
            'product_id': cls.product_2.id,
            'order_id': cls.purchase_order.id,
            'product_qty': 10,
            'price_unit': 50000,
            'product_uom': cls.product_uom.id,
            'date_planned': cls.today,
        })

        cls.purchase_order.button_confirm()

    def test_01_generate_analytic_lines(self):
        analytic_lines = self.purchase_order.mapped(
            'order_line.analytic_line_id')
        self.assertEqual(len(analytic_lines), 2)

        for line in analytic_lines:
            self.assertEqual(line.amount, 0)

        # 500 + 10 * 30
        self.assertEqual(sum(l.estimated_amount for l in analytic_lines), -800)

    def test_02_cancel_remove_analytic_line(self):
        self.purchase_order.button_cancel()
        analytic_lines = self.purchase_order.mapped(
            'order_line.analytic_line_id')
        self.assertEqual(len(analytic_lines), 0)
