# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoice_date = fields.Date(related="invoice_id.date_invoice", store=True)
    reference = fields.Char(related="invoice_id.reference", store=True)
