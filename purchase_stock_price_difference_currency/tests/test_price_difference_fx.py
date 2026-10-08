# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)
from odoo.tests import Form, tagged

from freezegun import freeze_time


@tagged("post_install", "-at_install")
class TestPriceDifferenceFx(ValuationReconciliationTestCommon):
    """Test the SRNF automated action shipped by this module.

    Scenario 1
    a purchase order in a foreign currency is received, then an exchange
    rate dated after the reception but no later than the reception date is
    added. On billing, native Odoo generates a price difference pair that is
    only a currency artifact. The automated action must neutralize that pair
    so that the exchange is handled by the native reconciliation (gain/loss
    account) and every entry is fully reconciled.
    """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company = cls.company_data["company"]
        cls.company.anglo_saxon_accounting = True

        # Route the price difference of the product category to its account.
        cls.price_diff_account = cls.company_data["default_account_stock_price_diff"]
        cls.stock_account_product_categ.property_account_creditor_price_difference_categ = (
            cls.price_diff_account
        )

        cls.foreign_currency = cls.currency_data["currency"]
        cls.company_currency = cls.company.currency_id
        cls.product = cls.test_product_delivery

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        company_data = super().setup_company_data(
            company_name, chart_template=chart_template, **kwargs
        )
        company_data["default_account_stock_price_diff"] = cls.env[
            "account.account"
        ].create(
            {
                "name": "default_account_stock_price_diff",
                "code": "STOCKDIFF",
                "reconcile": True,
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
                "company_id": company_data["company"].id,
            }
        )
        return company_data

    def _set_rate(self, date, rate):
        self.env["res.currency.rate"].create(
            {
                "name": date,
                "rate": rate,
                "currency_id": self.foreign_currency.id,
                "company_id": self.company.id,
            }
        )
        # Keep an explicit 1.0 rate for the company currency at the same date.
        self.env["res.currency.rate"].create(
            {
                "name": date,
                "rate": 1.0,
                "currency_id": self.company_currency.id,
                "company_id": self.company.id,
            }
        )

    def _create_purchase(self, date, quantity, price_unit):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "currency_id": self.foreign_currency.id,
                "date_order": date,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": quantity,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": price_unit,
                            "date_planned": date,
                        },
                    )
                ],
            }
        )
        order.button_confirm()
        return order

    def _create_invoice_for_po(self, purchase_order, date):
        move_form = Form(
            self.env["account.move"].with_context(
                default_move_type="in_invoice", default_date=date
            )
        )
        move_form.invoice_date = date
        move_form.partner_id = self.partner_a
        move_form.currency_id = self.foreign_currency
        move_form.purchase_id = purchase_order
        return move_form.save()

    @freeze_time("2021-01-10")
    def test_normal_flow(self):
        date_first_rate = "2021-01-01"
        date_receipt = "2021-01-05"
        date_later_rate = "2021-01-04"
        date_bill = "2021-01-05"
        quantity = 10.0
        price_unit = 100.0

        # 1 & 2 - Confirm the order in foreign currency and receive the stock.
        #         At reception only the first rate exists, so the layer is
        #         valued with it.
        self._set_rate(date_first_rate, 2.0)
        purchase_order = self._create_purchase(date_receipt, quantity, price_unit)
        with freeze_time(date_receipt):
            self._process_pickings(purchase_order.picking_ids, date=date_receipt)

        # 3 - Add a more recent rate, dated after the first rate but no later
        #     than the reception date. This is what turns the native
        #     reconversion into a price difference artifact.
        self._set_rate(date_later_rate, 2.5)

        # 3bis & 4 - Create the draft bill and post it (bill the order).
        invoice = self._create_invoice_for_po(purchase_order, date_bill)
        invoice.action_post()

        # 6 - Analyze the accounting entries.
        # The automated action removed the native price difference artifact.
        price_diff_lines = invoice.line_ids.filtered(
            lambda l: l.account_id == self.price_diff_account
        )
        self.assertFalse(
            price_diff_lines,
            "The native price difference pair should have been removed by the "
            "SRNF automated action (it was only a currency artifact).",
        )
        self.assertFalse(
            invoice.line_ids.filtered("is_anglo_saxon_line"),
            "No anglo-saxon price difference line should remain on the bill.",
        )

        # The action traces its correction in the chatter.
        self.assertTrue(
            invoice.message_ids.filtered(lambda m: "SRNF" in (m.body or "")),
            "The automated action should post a message on the bill.",
        )

        # 7 - Conclusion: the exchange goes through the native reconciliation
        #     (gain/loss account) and every entry is fully reconciled.
        picking = self.env["stock.picking"].search(
            [("purchase_id", "=", purchase_order.id)]
        )
        self.check_reconciliation(invoice, picking)

        interim_account = self.company_data["default_account_stock_in"]
        valuation_line = picking.move_lines.mapped(
            "account_move_ids.line_ids"
        ).filtered(lambda l: l.account_id == interim_account)
        self.assertTrue(
            valuation_line.full_reconcile_id,
            "The interim stock account should be fully reconciled.",
        )
        self.assertTrue(
            valuation_line.full_reconcile_id.exchange_move_id,
            "An exchange difference entry should have been generated "
            "(gain/loss on exchange).",
        )

        # 5 - Pay the bill.
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({})._create_payments()
        self.assertIn(
            invoice.payment_state,
            ("paid", "in_payment"),
            "The bill should be paid after registering the payment.",
        )
