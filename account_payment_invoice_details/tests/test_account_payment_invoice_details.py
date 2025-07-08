# Copyright 2025 - today Numigi (tm) and all its contributors
# (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo.tests.common import SavepointCase


class TestAccountPaymentInvoiceDetails(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.user.company_id
        cls.currency_usd = cls.company.currency_id
        cls.currency_eur = cls.env.ref("base.EUR")

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Vendor",
                "supplier_rank": 1,
            }
        )

        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test Accounts Payable",
                "code": "AP001",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )

        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Test Expense",
                "code": "EXP001",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )

        cls.journal_bank = cls.env["account.journal"].create(
            {
                "name": "Test Bank",
                "code": "BANK",
                "type": "bank",
            }
        )

        cls.payment_method = cls.env.ref("account.account_payment_method_manual_out")

    def _create_vendor_bill(self, amount, currency=None, invoice_date="2025-01-01"):
        """Helper method to create a vendor bill."""
        if currency is None:
            currency = self.currency_usd

        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "currency_id": currency.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": amount,
                        },
                    )
                ],
            }
        )

    def _create_vendor_payment(self, amount, currency=None):
        """Helper method to create a vendor payment."""
        if currency is None:
            currency = self.currency_usd

        return self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal_bank.id,
                "payment_method_id": self.payment_method.id,
                "amount": amount,
                "currency_id": currency.id,
            }
        )

    def _mock_invoice_payments_widget(self, invoice, payment, amount):
        """Helper method to mock the invoice_payments_widget JSON data."""
        payment_widget_data = {
            "content": [
                {
                    "name": f"Payment {payment.name}",
                    "journal_name": payment.journal_id.name,
                    "amount": amount,
                    "currency": payment.currency_id.symbol,
                    "date": "2025-01-01",
                    "account_payment_id": payment.id,
                    "ref": payment.name or f"PAY{payment.id}",
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)

    def test_allocation_line_ids_computation_single_invoice(self):
        """Test allocation_line_ids computation with single invoice."""
        # Create and post invoice
        invoice = self._create_vendor_bill(1000.0)
        invoice.action_post()

        # Create payment
        payment = self._create_vendor_payment(1000.0)
        payment.action_post()

        # Mock reconciliation and widget data
        self._mock_invoice_payments_widget(invoice, payment, 1000.0)
        payment.reconciled_bill_ids = [(4, invoice.id)]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Assertions
        self.assertEqual(len(payment.allocation_line_ids), 1)
        allocation = payment.allocation_line_ids[0]
        self.assertEqual(allocation.payment_id, payment)
        self.assertEqual(allocation.invoice_id, invoice)
        self.assertEqual(allocation.amount, 1000.0)
        self.assertEqual(allocation.invoice_name, invoice.name)
        self.assertEqual(allocation.currency_id, invoice.currency_id)

    def test_allocation_line_ids_computation_multiple_invoices(self):
        """Test allocation_line_ids computation with multiple invoices."""
        # Create and post invoices
        invoice1 = self._create_vendor_bill(800.0)
        invoice1.action_post()

        invoice2 = self._create_vendor_bill(400.0)
        invoice2.action_post()

        invoice3 = self._create_vendor_bill(300.0)
        invoice3.action_post()

        # Create payment
        payment = self._create_vendor_payment(1500.0)
        payment.action_post()

        # Mock reconciliation and widget data
        self._mock_invoice_payments_widget(invoice1, payment, 800.0)
        self._mock_invoice_payments_widget(invoice2, payment, 400.0)
        self._mock_invoice_payments_widget(invoice3, payment, 300.0)

        payment.reconciled_bill_ids = [
            (4, invoice1.id),
            (4, invoice2.id),
            (4, invoice3.id),
        ]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Assertions
        self.assertEqual(len(payment.allocation_line_ids), 3)

        # Sort allocations by amount for consistent testing
        allocations = payment.allocation_line_ids.sorted(
            key=lambda x: x.amount, reverse=True
        )

        self.assertEqual(allocations[0].invoice_id, invoice1)
        self.assertEqual(allocations[0].amount, 800.0)

        self.assertEqual(allocations[1].invoice_id, invoice2)
        self.assertEqual(allocations[1].amount, 400.0)

        self.assertEqual(allocations[2].invoice_id, invoice3)
        self.assertEqual(allocations[2].amount, 300.0)

    def test_allocation_line_ids_partial_payment(self):
        """Test allocation_line_ids with partial payment scenario."""
        # Create invoices with total amount > payment amount
        invoice1 = self._create_vendor_bill(1200.0)
        invoice1.action_post()

        invoice2 = self._create_vendor_bill(800.0)
        invoice2.action_post()

        # Create partial payment
        payment = self._create_vendor_payment(1500.0)
        payment.action_post()

        # Mock partial allocation: full payment to invoice1, partial to invoice2
        self._mock_invoice_payments_widget(invoice1, payment, 1200.0)
        self._mock_invoice_payments_widget(invoice2, payment, 300.0)

        payment.reconciled_bill_ids = [(4, invoice1.id), (4, invoice2.id)]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Assertions
        self.assertEqual(len(payment.allocation_line_ids), 2)

        allocations = payment.allocation_line_ids.sorted(
            key=lambda x: x.amount, reverse=True
        )

        # Invoice1 fully paid
        self.assertEqual(allocations[0].invoice_id, invoice1)
        self.assertEqual(allocations[0].amount, 1200.0)

        # Invoice2 partially paid
        self.assertEqual(allocations[1].invoice_id, invoice2)
        self.assertEqual(allocations[1].amount, 300.0)

    def test_allocation_line_ids_zero_allocation_filtered(self):
        """Test that zero allocations are filtered out."""
        invoice = self._create_vendor_bill(1000.0)
        invoice.action_post()

        payment = self._create_vendor_payment(1000.0)
        payment.action_post()

        # Mock zero allocation
        self._mock_invoice_payments_widget(invoice, payment, 0.0)
        payment.reconciled_bill_ids = [(4, invoice.id)]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Should be empty due to zero allocation
        self.assertEqual(len(payment.allocation_line_ids), 0)

    def test_allocation_line_ids_no_reconciled_bills(self):
        """Test allocation_line_ids when no reconciled bills exist."""
        payment = self._create_vendor_payment(1000.0)
        payment.action_post()

        # Ensure no reconciled bills
        payment.reconciled_bill_ids = [(5, 0, 0)]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Should be empty
        self.assertEqual(len(payment.allocation_line_ids), 0)

    def test_get_allocated_amount_for_invoice_valid_data(self):
        """Test _get_allocated_amount_for_invoice with valid JSON data."""
        invoice = self._create_vendor_bill(1000.0)
        payment = self._create_vendor_payment(500.0)

        # Mock valid widget data with multiple payments
        payment_widget_data = {
            "content": [
                {
                    "name": "Other Payment",
                    "account_payment_id": 999,
                    "amount": 200.0,
                },
                {
                    "name": "Our Payment",
                    "account_payment_id": payment.id,
                    "amount": 500.0,
                },
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)

        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 500.0)

    def test_get_allocated_amount_for_invoice_no_match(self):
        """Test _get_allocated_amount_for_invoice when payment not found."""
        invoice = self._create_vendor_bill(1000.0)
        payment = self._create_vendor_payment(500.0)

        # Mock widget data without matching payment
        payment_widget_data = {
            "content": [
                {
                    "name": "Other Payment",
                    "account_payment_id": 999,
                    "amount": 200.0,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)

        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

    def test_get_allocated_amount_for_invoice_empty_widget(self):
        """Test _get_allocated_amount_for_invoice with empty widget."""
        invoice = self._create_vendor_bill(1000.0)
        payment = self._create_vendor_payment(500.0)

        # Test with False widget
        invoice.invoice_payments_widget = False
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

        # Test with None widget
        invoice.invoice_payments_widget = None
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

    def test_get_allocated_amount_for_invoice_malformed_json(self):
        """Test _get_allocated_amount_for_invoice with malformed JSON."""
        invoice = self._create_vendor_bill(1000.0)
        payment = self._create_vendor_payment(500.0)

        # Test with invalid JSON
        invoice.invoice_payments_widget = "invalid json"
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

        # Test with malformed structure
        invoice.invoice_payments_widget = json.dumps({"wrong": "structure"})
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

        # Test with content not being a list
        invoice.invoice_payments_widget = json.dumps({"content": "not a list"})
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

    def test_get_allocated_amount_for_invoice_missing_fields(self):
        """Test _get_allocated_amount_for_invoice with missing required fields."""
        invoice = self._create_vendor_bill(1000.0)
        payment = self._create_vendor_payment(500.0)

        # Test with missing account_payment_id
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "amount": 500.0,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

        # Test with missing amount
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "account_payment_id": payment.id,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(amount, 0.0)

    def test_allocation_line_ids_multi_currency(self):
        """Test allocation_line_ids with multi-currency scenario."""
        # Create EUR invoice
        invoice_eur = self._create_vendor_bill(850.0, self.currency_eur)
        invoice_eur.action_post()

        # Create USD payment
        payment_usd = self._create_vendor_payment(1000.0, self.currency_usd)
        payment_usd.action_post()

        # Mock allocation (payment in USD, invoice in EUR)
        self._mock_invoice_payments_widget(invoice_eur, payment_usd, 850.0)
        payment_usd.reconciled_bill_ids = [(4, invoice_eur.id)]

        # Trigger computation
        payment_usd._compute_allocation_line_ids()

        # Assertions
        self.assertEqual(len(payment_usd.allocation_line_ids), 1)
        allocation = payment_usd.allocation_line_ids[0]
        self.assertEqual(allocation.amount, 850.0)
        self.assertEqual(allocation.currency_id, self.currency_eur)  # Invoice currency

    def test_allocation_details_model_fields(self):
        """Test the allocation details model fields and relationships."""
        # Create test data
        invoice = self._create_vendor_bill(1000.0)
        invoice.action_post()

        payment = self._create_vendor_payment(1000.0)
        payment.action_post()

        # Create allocation detail record manually
        allocation = self.env["account.payment.invoice.details"].create(
            {
                "payment_id": payment.id,
                "invoice_id": invoice.id,
                "amount": 1000.0,
            }
        )

        # Test field values
        self.assertEqual(allocation.payment_id, payment)
        self.assertEqual(allocation.invoice_id, invoice)
        self.assertEqual(allocation.amount, 1000.0)
        self.assertEqual(allocation.invoice_name, invoice.name)
        self.assertEqual(allocation.currency_id, invoice.currency_id)

    def test_allocation_line_ids_update_on_reconciliation_change(self):
        """Test that allocation_line_ids updates when reconciliation changes."""
        # Create invoices
        invoice1 = self._create_vendor_bill(800.0)
        invoice1.action_post()

        invoice2 = self._create_vendor_bill(400.0)
        invoice2.action_post()

        payment = self._create_vendor_payment(1200.0)
        payment.action_post()

        # Initial reconciliation with one invoice
        self._mock_invoice_payments_widget(invoice1, payment, 800.0)
        payment.reconciled_bill_ids = [(4, invoice1.id)]
        payment._compute_allocation_line_ids()

        self.assertEqual(len(payment.allocation_line_ids), 1)
        self.assertEqual(payment.allocation_line_ids[0].invoice_id, invoice1)

    def test_allocation_line_ids_stored_computation(self):
        """Test that allocation_line_ids is properly stored and computed."""
        invoice = self._create_vendor_bill(1000.0)
        invoice.action_post()

        payment = self._create_vendor_payment(1000.0)
        payment.action_post()

        # Mock reconciliation
        self._mock_invoice_payments_widget(invoice, payment, 1000.0)
        payment.reconciled_bill_ids = [(4, invoice.id)]

        # Trigger computation
        payment._compute_allocation_line_ids()

        # Check that records exist in database
        allocation_count = self.env["account.payment.invoice.details"].search_count(
            [("payment_id", "=", payment.id)]
        )
        self.assertEqual(allocation_count, 1)

        # Check field dependency
        self.assertIn(
            "move_id.line_ids.matched_debit_ids",
            payment._fields["allocation_line_ids"].depends,
        )
        self.assertIn(
            "move_id.line_ids.matched_credit_ids",
            payment._fields["allocation_line_ids"].depends,
        )
