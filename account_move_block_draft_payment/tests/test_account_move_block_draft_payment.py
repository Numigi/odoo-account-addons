# Copyright 2026 Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError
import pytest


@pytest.mark.common
class TestAccountMoveBlockDraftPayment(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product = self.env["product.product"].create({"name": "Test Product"})

    def _create_draft_invoice(self):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (0, 0, {"product_id": self.product.id, "price_unit": 100.0})
                ],
            }
        )

    def _create_posted_invoice(self):
        invoice = self._create_draft_invoice()
        invoice.action_post()
        return invoice

    def _create_cancelled_invoice(self):
        invoice = self._create_draft_invoice()
        invoice.button_cancel()
        return invoice

    def test_payment_on_draft_invoice_raises_error(self):
        invoice = self._create_draft_invoice()
        with pytest.raises(ValidationError):
            invoice.action_register_payment()

    def test_payment_on_cancelled_invoice_raises_error(self):
        invoice = self._create_cancelled_invoice()
        with pytest.raises(ValidationError):
            invoice.action_register_payment()

    def test_payment_on_posted_invoice_succeeds(self):
        invoice = self._create_posted_invoice()
        action_result = invoice.action_register_payment()
        assert action_result["res_model"] == "account.payment.register"
