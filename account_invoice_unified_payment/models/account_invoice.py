# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def reconcile_and_open_payment(self):
        self._check_invoices_can_be_reconciled()

        lines = self.mapped("move_id.line_ids").filtered(
            lambda l: l.account_id.internal_type in ("payable", "receivable")
        )
        lines.reconcile()

        return self._open_payment_action()

    def _open_payment_action(self):
        invoice_ids = self.filtered(lambda i: i.state != "paid").ids
        action = self.env["account.register.payments"].get_formview_action()
        action["context"] = {
            "active_model": "account.invoice",
            "active_ids": invoice_ids,
        }
        action["target"] = "new"
        return action

    def _check_invoices_can_be_reconciled(self):
        self._check_invoice_versus_refund_residuals()

        for invoice in self:
            if invoice.state != "open":
                self._raise_can_not_reconcile_error(
                    _(
                        "The invoice {} is not open.",
                    ).format(invoice.display_name)
                )

        currencies = self.mapped("currency_id")
        if len(currencies) > 1:
            self._raise_can_not_reconcile_error(
                _(
                    "These are in multiple currencies ({}).",
                ).format(", ".join(currencies.mapped("name")))
            )

        partners = self.mapped("commercial_partner_id")
        if len(partners) > 1:
            self._raise_can_not_reconcile_error(
                _(
                    "These belong to multiple commercial partners ({}).",
                ).format(", ".join(partners.mapped("display_name")))
            )

        accounts = self.mapped("account_id")
        if len(accounts) > 1:
            self._raise_can_not_reconcile_error(
                _(
                    "These have different accounts defined ({}).",
                ).format(", ".join(accounts.mapped("display_name")))
            )

    def _check_invoice_versus_refund_residuals(self):
        invoices = self.filtered(lambda i: "invoice" in i.type)
        refunds = self - invoices

        invoice_residual = sum(invoices.mapped("residual"))
        refund_residual = sum(refunds.mapped("residual"))

        if invoice_residual < refund_residual:
            self._raise_can_not_reconcile_error(
                _(
                    "The open balance of invoices ({invoice_residual}) must "
                    "strictly be higher than the open balance of refunds ({refund_residual}).",
                ).format(
                    invoice_residual=invoice_residual, refund_residual=refund_residual
                )
            )

    def _raise_can_not_reconcile_error(self, message):
        raise ValidationError(
            _("You may not reconcile the selected invoices and refunds.\n") + message
        )
