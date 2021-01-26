# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if not (vals.get("statement_line_id") or vals.get("full_reconcile_id")):
            return res
        for line in self.filtered(
            lambda r: r.statement_line_id and r.full_reconcile_id
        ):
            for move in line.full_reconcile_id.reconciled_line_ids.mapped("move_id"):
                if move.is_reversal_move() or move.is_reversed_move():
                    raise UserError(
                        _(
                            "The selected accounting entry is already reversed or is "
                            "the reversal of another entry. You must select another "
                            "line."
                        )
                    )
        return res
