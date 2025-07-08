# Copyright 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_account_payment_details(self):
        """
        Get detailed payment allocation information for vendor bills only.

        This function specifically works with vendor bill payments (supplier invoices)
        by iterating through reconciled_bill_ids field which contains only vendor bills.
        Customer invoices are handled through reconciled_invoice_ids and are not
        processed by this function.

        Returns:
            list: List of dictionaries containing vendor bill details and allocated amounts
                  [
                      {
                          'invoice_id': int,          # ID of the vendor bill
                          'invoice': str,             # Name/number of the vendor bill
                          'amount': float,            # Allocated amount for this bill
                          'currency_id': str          # Currency name
                      },
                      ...
                  ]

        Note:
            - Only processes vendor bills (move_type='in_invoice')
            - Filters out zero allocations automatically
            - Handles malformed JSON gracefully
        """
        details = []
        for invoice in self.reconciled_bill_ids:
            allocated_amount = self._get_allocated_amount_for_invoice(invoice)
            if allocated_amount:
                details.append(
                    {
                        "invoice_id": invoice.id,
                        "invoice": invoice.name,
                        "amount": allocated_amount,
                        "currency_id": invoice.currency_id.name,
                    }
                )
        return details

    def _get_allocated_amount_for_invoice(self, invoice):
        """
        Extract allocated amount from invoice_payments_widget for this payment.

        This helper function parses the JSON data in the invoice_payments_widget
        field to find the payment entry matching the current payment ID and
        extracts the allocated amount.

        Args:
            invoice (account.move): The vendor bill record to extract allocation from

        Returns:
            float: The allocated amount for this payment, or 0.0 if:
                   - No payment widget data exists
                   - JSON is malformed
                   - Payment not found in widget
                   - Amount is missing or invalid
        """
        if not invoice.invoice_payments_widget:
            return 0.0

        try:
            payments_data = json.loads(invoice.invoice_payments_widget)
            content = payments_data.get("content", [])

            for payment_data in content:
                if payment_data.get("account_payment_id") == self.id:
                    return payment_data.get("amount", 0.0)
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

        return 0.0
