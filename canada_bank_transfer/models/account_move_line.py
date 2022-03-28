# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        self._set_payment_state_recconciled(vals)

    @api.multi
    def _set_payment_state_recconciled(self, vals):
        if "full_reconcile_id" in vals and vals["full_reconcile_id"]:
            self.env["account.full.reconcile"].browse(
                vals["full_reconcile_id"]
            ).reconciled_line_ids.mapped("payment_id").filtered(
                lambda payment: payment.is_eft_payment
            ).write(
                {"state": "reconciled"}
            )
