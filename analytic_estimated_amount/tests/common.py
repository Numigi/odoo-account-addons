# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests import common


class TestSaleOrderBase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderBase, cls).setUpClass()
        cls.today = datetime.now()
        cls.partner = cls.env['res.partner'].create({
            'name': 'J. Gama Inc.',
            'is_company': True,
        })

        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Equipments',
        })

        cls.product_1 = cls.env['product.product'].create({
            'name': 'Product 1',
            'type': 'product',
        })

        cls.product_2 = cls.env['product.product'].create({
            'name': 'Product 2',
            'type': 'product',
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })

        cls.line_1 = cls.env['sale.order.line'].create({
            'product_id': cls.product_1.id,
            'order_id': cls.sale_order.id,
            'product_uom_qty': 1,
            'price_unit': 1000.00,
        })

        cls.line_2 = cls.env['sale.order.line'].create({
            'product_id': cls.product_2.id,
            'order_id': cls.sale_order.id,
            'product_uom_qty': 10,
            'price_unit': 50.00,
        })
