# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import AccessError


class AccountMove(models.Model):

    _inherit = "account.move"

    def button_draft(self):
        if self._contains_payments() and not self._user_can_cancel_payments():
            raise AccessError(_("You are not authorized to cancel payments."))

        return super().button_draft()

    def _user_can_cancel_payments(self):
        return self.env.user.has_group(
            "account_payment_cancel_group.group_cancel_payments"
        )

    def _contains_payments(self):
        return self and bool(
            self.env["account.payment"].search([("move_id", "in", self.ids)])
        )
