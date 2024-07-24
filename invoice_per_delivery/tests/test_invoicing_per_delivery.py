# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale.tests.common import TestSaleCommon
from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestSaleStock(TestSaleCommon):

    def test_00_sale_stock_invoice(self):
        self.partner_a.write({"invoice_per_delivery": True})
        self.product = self.company_data["product_delivery_sales_price"]
        so_vals = {
            "partner_id": self.partner_a.id,
            "partner_invoice_id": self.partner_a.id,
            "partner_shipping_id": self.partner_a.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.company_data["default_pricelist"].id,
        }
        self.so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()
        self.assertTrue(
            self.so.picking_ids,
            'Sale Stock: no picking created for "invoice on delivery" storable products',
        )

        pick = self.so.picking_ids
        pick.move_lines.write({"quantity_done": 1})
        wiz_act = pick.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"])
        ).save()
        wiz.process()

        self.assertTrue(
            self.so.invoice_ids,
            "No invoice is liked to the so after validating the delivery order",
        )
        self.assertEqual(
            self.so.invoice_ids[0].state,
            "draft",
            "Invoice created in draft status after validating the delivery order",
        )
        self.assertEqual(
            self.so.invoice_status,
            "no",
            'so invoice_status should be "no" instead of "%s"'
            % self.so.invoice_status,
        )
        self.assertTrue(
            self.so.invoice_ids.mapped("picking_ids"),
            "No piking is linked to the invoice after validating the delivery order",
        )
