# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo.tests.common import SavepointCase


class TestAccountPaymentAllocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.user.company_id
        cls.currency = cls.company.currency_id

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

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Bank",
                "code": "BANK",
                "type": "bank",
            }
        )

        cls.payment_method = cls.env.ref("account.account_payment_method_manual_out")

    def test_get_account_payment_details(self):
        """Test the _get_account_payment_details method"""
        # Create invoices
        invoice1 = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product 1",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 1000.0,
                        },
                    )
                ],
                "invoice_date": "2025-01-01",
            }
        )
        invoice1.action_post()

        invoice2 = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product 2",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 500.0,
                        },
                    )
                ],
                "invoice_date": "2025-01-01",
            }
        )
        invoice2.action_post()

        # Create a payment
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 1500.0,
                "currency_id": self.currency.id,
            }
        )
        payment.action_post()

        # Mock the invoice_payments_widget with test data
        payment_widget_data1 = {
            "content": [
                {
                    "name": "Test Payment",
                    "journal_name": "Test Bank",
                    "amount": 1000.0,
                    "currency": "$",
                    "date": "2025-01-01",
                    "payment_id": 12345,
                    "account_payment_id": payment.id,
                    "ref": "PAY001",
                }
            ]
        }
        invoice1.invoice_payments_widget = json.dumps(payment_widget_data1)

        payment_widget_data2 = {
            "content": [
                {
                    "name": "Test Payment",
                    "journal_name": "Test Bank",
                    "amount": 500.0,
                    "currency": "$",
                    "date": "2025-01-01",
                    "payment_id": 12345,
                    "account_payment_id": payment.id,
                    "ref": "PAY001",
                }
            ]
        }
        invoice2.invoice_payments_widget = json.dumps(payment_widget_data2)

        # Mock reconciled_bill_ids
        payment.reconciled_bill_ids = [(4, invoice1.id), (4, invoice2.id)]

        # Test the payment details function
        details = payment._get_account_payment_details()

        self.assertEqual(len(details), 2)

        # Sort by invoice id for consistent testing
        details.sort(key=lambda x: x["invoice"].id)

        # Check that we get dictionaries with invoice objects and amounts
        self.assertIsInstance(details[0], dict)
        self.assertIsInstance(details[1], dict)

        # Verify the structure of returned data
        self.assertIn("invoice", details[0])
        self.assertIn("amount", details[0])
        self.assertIn("invoice", details[1])
        self.assertIn("amount", details[1])

        # Check that invoice objects are correct
        invoices_in_details = [detail["invoice"] for detail in details]
        self.assertIn(invoice1, invoices_in_details)
        self.assertIn(invoice2, invoices_in_details)

        # Verify the allocated amounts are correct
        detail1 = next(d for d in details if d["invoice"] == invoice1)
        detail2 = next(d for d in details if d["invoice"] == invoice2)

        self.assertEqual(detail1["amount"], 1000.0)
        self.assertEqual(detail2["amount"], 500.0)

    def test_get_allocated_amount_for_invoice(self):
        """Test the _get_allocated_amount_for_invoice method"""
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 500.0,
                "currency_id": self.currency.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 1000.0,
                        },
                    )
                ],
            }
        )

        # Test with valid JSON data
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

        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 500.0)

        # Test with no matching payment
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

        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

        # Test with invalid JSON
        invoice.invoice_payments_widget = "invalid json"
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

        # Test with empty widget
        invoice.invoice_payments_widget = False
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

    def test_get_account_payment_details_empty_reconciled_bills(self):
        """Test _get_account_payment_details when no reconciled bills exist"""
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 1000.0,
                "currency_id": self.currency.id,
            }
        )

        # Ensure no reconciled bills
        payment.reconciled_bill_ids = [(5, 0, 0)]

        details = payment._get_account_payment_details()
        self.assertEqual(len(details), 0)

    def test_get_account_payment_details_with_zero_allocation(self):
        """Test _get_account_payment_details filters out zero allocations"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 1000.0,
                        },
                    )
                ],
                "invoice_date": "2025-01-01",
            }
        )
        invoice.action_post()

        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 1000.0,
                "currency_id": self.currency.id,
            }
        )

        # Mock widget with zero amount
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "account_payment_id": payment.id,
                    "amount": 0.0,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        payment.reconciled_bill_ids = [(4, invoice.id)]

        details = payment._get_account_payment_details()
        self.assertEqual(len(details), 0)

    def test_get_allocated_amount_malformed_json_structures(self):
        """Test _get_allocated_amount_for_invoice with various malformed JSON"""
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 500.0,
                "currency_id": self.currency.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 1000.0,
                        },
                    )
                ],
            }
        )

        # Test with missing content key
        payment_widget_data = {"other_key": "value"}
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

        # Test with content not being a list
        payment_widget_data = {"content": "not a list"}
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

        # Test with content item missing account_payment_id
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "amount": 500.0,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

        # Test with content item missing amount
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "account_payment_id": payment.id,
                }
            ]
        }
        invoice.invoice_payments_widget = json.dumps(payment_widget_data)
        allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
        self.assertEqual(allocated_amount, 0.0)

    def test_get_account_payment_details_only_vendor_bills(self):
        """Test that the function only works with vendor bills (in_invoice)"""
        # Create a customer invoice (should not be included)
        customer_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 1000.0,
                        },
                    )
                ],
                "invoice_date": "2025-01-01",
            }
        )
        customer_invoice.action_post()

        # Create a vendor bill
        vendor_bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "account_id": self.account_expense.id,
                            "quantity": 1,
                            "price_unit": 500.0,
                        },
                    )
                ],
                "invoice_date": "2025-01-01",
            }
        )
        vendor_bill.action_post()

        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "payment_method_id": self.payment_method.id,
                "amount": 1500.0,
                "currency_id": self.currency.id,
            }
        )

        # Mock widget data for vendor bill only
        payment_widget_data = {
            "content": [
                {
                    "name": "Test Payment",
                    "account_payment_id": payment.id,
                    "amount": 500.0,
                }
            ]
        }
        vendor_bill.invoice_payments_widget = json.dumps(payment_widget_data)

        # The function uses reconciled_bill_ids, which typically only includes vendor bills
        payment.reconciled_bill_ids = [(4, vendor_bill.id)]

        details = payment._get_account_payment_details()
        self.assertEqual(len(details), 1)
        self.assertIsInstance(details[0], dict)
        self.assertIn("invoice", details[0])
        self.assertIn("amount", details[0])
        self.assertEqual(details[0]["invoice"].id, vendor_bill.id)
        self.assertEqual(details[0]["amount"], 500.0)
