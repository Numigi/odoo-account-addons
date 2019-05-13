# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class Invoice(models.Model):
    """Add the missing field amount_tax_signed to invoices."""

    _inherit = 'account.invoice'

    amount_tax_signed = fields.Monetary(
        string='Tax Amount Signed', store=True,
        compute='_compute_amount_tax_signed')

    @api.depends('amount_tax', 'type')
    def _compute_amount_tax_signed(self):
        for invoice in self:
            sign = invoice.type in ['in_refund', 'out_refund'] and -1 or 1
            invoice.amount_tax_signed = invoice.amount_tax * sign
