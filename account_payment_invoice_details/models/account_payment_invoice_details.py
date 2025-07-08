# Copyright 2025 - today Numigi (tm) and all its contributors
# (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountPaymentInvoiceDetails(models.Model):
    _name = "account.payment.invoice.details"
    _description = "Payment Invoice Allocation Details"
    _order = "payment_id, invoice_id"

    payment_id = fields.Many2one(
        "account.payment", string="Payment", required=True, ondelete="cascade"
    )
    invoice_id = fields.Many2one(
        "account.move", string="Invoice", required=True, ondelete="cascade"
    )
    invoice_name = fields.Char(
        string="Invoice Number", related="invoice_id.name", readonly=True
    )
    amount = fields.Float(string="Allocated Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="invoice_id.currency_id",
        readonly=True,
    )
