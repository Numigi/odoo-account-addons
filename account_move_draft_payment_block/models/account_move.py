# -*- coding: utf-8 -*-
# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_force_register_payment(self):
        self._verify_moves_are_posted()
        return super().action_force_register_payment()

    def button_draft(self):
        self._verify_no_linked_payments()
        return super().button_draft()

    def _verify_moves_are_posted(self):
        unposted_moves = self.filtered(lambda m: m.state != "posted")
        if unposted_moves:
            raise ValidationError(
                _("You cannot register a payment for an unposted invoice.")
            )

    def _verify_no_linked_payments(self):
        invoices = self.filtered(lambda m: m.is_invoice())
        invoices_with_payments = invoices.filtered(lambda m: m.matched_payment_ids)
        if invoices_with_payments:
            raise ValidationError(
                _(
                    "It is impossible to reset this invoice to draft because "
                    "one or more payments are associated with it. "
                    "Please cancel the concerned payments first."
                )
            )
