# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoice_date = fields.Date(related="invoice_id.date_invoice", store=True)
    # old field to remove
    invoice_reference = fields.Char()
    invoice_ref = fields.Char(compute="_compute_invoice_reference",
                              string="Invoice Reference",
                              store=True)

    @api.depends("invoice_id", "invoice_id.reference")
    def _compute_invoice_reference(self):
        for rec in self:
            if rec.invoice_id:
                rec.invoice_ref = rec.invoice_id.reference
