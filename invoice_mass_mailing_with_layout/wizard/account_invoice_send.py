# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountInvoiceSend(models.TransientModel):

    _inherit = "account.invoice.send"

    def send_and_print_action(self):
        self.ensure_one()

        if self.composition_mode == "mass_mail":
            for invoice in self.invoice_ids:
                self._send_single_invoice(invoice)
        else:
            return super().send_and_print_action()

    def _send_single_invoice(self, invoice):
        context = {
            "mark_invoice_as_sent": True,
            "active_ids": [invoice.id],
            "active_id": invoice.id,
            "active_model": "account.move",
        }
        self = self.with_context(context)
        self.composer_id = self.env["mail.compose.message"].create(
            {"composition_mode": "comment"}
        )
        self.invoice_ids = invoice
        self.onchange_template_id()
        self.send_and_print_action()

    def _send_email(self):
        self = self.with_context(
            custom_layout="mail.mail_notification_paynow",
            lang=self.invoice_ids[:1].partner_id.lang,
        )
        return super(AccountInvoiceSend, self)._send_email()
