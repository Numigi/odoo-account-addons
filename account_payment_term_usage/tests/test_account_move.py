# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data, unpack
from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


@ddt
class TestAccountMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Journal", "type": "purchase", "code": "SAJ",}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "journal_id": cls.journal.id,
                "move_type": "in_invoice",
            }
        )
        terms = cls.env["account.payment.term"].search([])
        cls.term_sale = terms[0]
        cls.term_sale.usage = "sale"
        cls.term_purchase = terms[1]
        cls.term_purchase.usage = "purchase"
        cls.term_sale_and_purchase = terms[2]
        cls.term_sale_and_purchase.usage = "sale_and_purchase"

    # @data(
    #     ("in_invoice", "purchase"),
    #     ("in_refund", "purchase"),
    #     ("out_invoice", "sale"),
    #     ("out_refund", "sale"),
    # )
    # @unpack
    # def test_payment_term_usage(self, move_type, usage):
    #     self.invoice.move_type = move_type
    #     self.journal.type = usage
    #     assert self.invoice.payment_term_usage == usage

    def test_sale_and_purchase(self):
        terms = (
            self.env["account.payment.term"]
            .with_context(enabled_payment_term_usage=False)
            .search([])
        )
        assert self.term_sale in terms
        assert self.term_purchase in terms
        assert self.term_sale_and_purchase in terms

    def test_sale_enabled(self):
        terms = (
            self.env["account.payment.term"]
            .with_context(enabled_payment_term_usage="sale")
            .search([])
        )
        assert self.term_sale in terms
        assert self.term_purchase not in terms
        assert self.term_sale_and_purchase in terms

    def test_purchase_enabled(self):
        terms = (
            self.env["account.payment.term"]
            .with_context(enabled_payment_term_usage="purchase")
            .search([])
        )
        assert self.term_sale not in terms
        assert self.term_purchase in terms
        assert self.term_sale_and_purchase in terms
