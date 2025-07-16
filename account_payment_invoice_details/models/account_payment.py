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
        by iterating through reconciled_bill_id.

        Returns: list
        """
        details = []
        for invoice in self.reconciled_bill_ids:
            allocated_amount = self._get_allocated_amount_for_invoice(invoice)
            if allocated_amount:
                details.append(
                    {
                        "invoice": invoice,
                        "amount": allocated_amount,
                    }
                )
        return details

    def _get_allocated_amount_for_invoice(self, invoice):
        """
        Extract allocated amount from invoice_payments_widget for this payment.
        Returns: float:
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
