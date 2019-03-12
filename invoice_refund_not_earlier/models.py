# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class Invoice(models.Model):

    _inherit = 'account.invoice'

    def _is_refund_prior_to_invoice(self):
        """Return whether the object is a refund prior to the invoice date.

        :rtype: bool
        """
        return (
            self.type in ('in_refund', 'out_refund') and
            self.refund_invoice_id and
            (self.date_invoice and self.date_invoice < self.refund_invoice_id.date_invoice or
             self.date and self.date < self.refund_invoice_id.date_invoice)
        )

    @api.multi
    def action_invoice_open(self):
        invalid_refunds = self.filtered(lambda inv: inv._is_refund_prior_to_invoice())
        if invalid_refunds:
            refund = invalid_refunds[0]
            invoice = refund.refund_invoice_id
            raise ValidationError(_(
                "The refund date ({refund_date}) or the accounting date ({accounting_date}) "
                "of the refund ({refund}) can not "
                "be prior to the date ({invoice_date}) of the invoice ({invoice})."
            ).format(
                refund_date=refund.date_invoice or _('empty'),
                accounting_date=refund.date or _('empty'),
                refund=refund.display_name,
                invoice_date=invoice.date_invoice,
                invoice=invoice.display_name,
            ))
        return super().action_invoice_open()
