# Copyright 2025 - today Numigi (tm) and all its contributors
# (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    allocation_line_ids = fields.One2many(
        "account.payment.invoice.details",
        "payment_id",
        string="Allocation Lines",
        compute="_compute_allocation_line_ids",
        store=True,
        help="Payment allocation details for reconciled invoices",
    )

    @api.depends(
        "move_id.line_ids.matched_debit_ids", "move_id.line_ids.matched_credit_ids"
    )
    def _compute_allocation_line_ids(self):
        """Compute allocation lines based on reconciled bills."""
        for payment in self:
            allocation_lines = []
            for invoice in payment.reconciled_bill_ids:
                allocated_amount = payment._get_allocated_amount_for_invoice(invoice)
                if allocated_amount:
                    allocation_lines.append(
                        (
                            0,
                            0,
                            {
                                "payment_id": payment.id,
                                "invoice_id": invoice.id,
                                "amount": allocated_amount,
                            },
                        )
                    )

            payment.allocation_line_ids = allocation_lines

    def _get_allocated_amount_for_invoice(self, invoice):
        """Extract allocated amount from invoice_payments_widget JSON field.

        :param invoice: The invoice record
        :return: float
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
