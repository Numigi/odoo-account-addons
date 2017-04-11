# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from . import common


class TestSaleOrder(common.TestSaleOrderBase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.sale_order.action_confirm()
        cls.sale_order._create_analytic_account()

    def test_01_generate_analytic_line(self):
        analytic_lines = self.sale_order.mapped('order_line.analytic_line_id')

        for line in analytic_lines:
            self.assertEqual(line.amount, 0)

        # 1000 + 50 * 10
        self.assertEqual(sum(l.estimated_amount for l in analytic_lines), 1500)

    def test_02_cancel_remove_analytic_line(self):
        self.sale_order.action_cancel()
        analytic_lines = self.sale_order.mapped('order_line.analytic_line_id')
        self.assertEqual(len(analytic_lines), 0)
