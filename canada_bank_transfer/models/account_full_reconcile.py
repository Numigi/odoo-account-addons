# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountFullReconcile(models.Model):

    _inherit = "account.full.reconcile"

    @api.multi
    def unlink(self):
        self._set_payment_state_sent()
        return super(AccountFullReconcile, self).unlink()

    @api.multi
    def _set_payment_state_sent(self):
        self.mapped("reconciled_line_ids").mapped("payment_id").filtered(
            lambda payment: payment.is_eft_payment
        ).write({"state": "sent"})
