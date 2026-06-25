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

    def _create_invoice(self):
        # Creates a standard draft invoice (also valid for down payments logic)
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (0, 0, {"product_id": self.product.id, "price_unit": 100.0})
                ],
            }
        )

    def _post_invoice(self, invoice):
        invoice.action_post()
        return invoice

    def _register_payment(self, invoice):
        # Simulates the payment registration wizard
        payment_register = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create({})
        )
        payment_register._create_payments()

    def test_payment_on_draft_invoice_raises_error(self):
        invoice = self._create_invoice()
        with pytest.raises(ValidationError):
            invoice.action_force_register_payment()

    def test_payment_on_cancelled_invoice_raises_error(self):
        invoice = self._create_invoice()
        invoice.button_cancel()
        with pytest.raises(ValidationError):
            invoice.action_force_register_payment()

    def test_payment_on_posted_invoice_succeeds(self):
        invoice = self._create_invoice()
        self._post_invoice(invoice)
        action_result = invoice.action_force_register_payment()
        assert action_result["res_model"] == "account.payment.register"

    def test_payment_creation_on_posted_invoice(self):
        invoice = self._create_invoice()
        self._post_invoice(invoice)
        self._register_payment(invoice)
        assert invoice.payment_state in ("in_payment", "paid")

    def test_reset_to_draft_without_payment_succeeds(self):
        invoice = self._create_invoice()
        self._post_invoice(invoice)
        invoice.button_draft()
        assert invoice.state == "draft"

    def test_reset_to_draft_with_payment_raises_error(self):
        invoice = self._create_invoice()
        self._post_invoice(invoice)
        self._register_payment(invoice)

        with pytest.raises(ValidationError):
            invoice.button_draft()

    def test_reset_to_draft_with_blocked_payment_state_succeeds(self):
        # An invoice manually flagged as 'blocked' has no associated payment;
        # resetting it to draft must remain allowed.
        invoice = self._create_invoice()
        self._post_invoice(invoice)
        invoice.payment_state = "blocked"
        invoice.button_draft()
        assert invoice.state == "draft"
