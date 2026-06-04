# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import AccessError


class AccountMove(models.Model):

    _inherit = "account.move"

    def button_draft(self):
        self._check_payment_cancel_authorization()
        return super().button_draft()

    def button_cancel(self):
        self._check_payment_cancel_authorization()
        return super().button_cancel()

    def _check_payment_cancel_authorization(self):
        if self._contains_payments() and not self._user_can_cancel_payments():
            raise AccessError(
                _("You are not authorized to reset to draft or cancel payments.")
            )

    def _user_can_cancel_payments(self):
        return self.env.user.has_group(
            "account_payment_cancel_group.group_cancel_payments"
        )

    def _contains_payments(self):
        return self and bool(
            self.env["account.payment"].search([("move_id", "in", self.ids)])
        )
