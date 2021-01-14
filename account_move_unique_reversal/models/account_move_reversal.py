# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.multi
    def reverse_moves(self):
        self.ensure_one()
        move_env = self.env["account.move"]
        move = move_env.browse(self._context.get("active_ids"))
        if move.reverse_entry_id:
            raise UserError(
                _(
                    "The accounting entry {} is already reversed (by entry {}). "
                    "You can only reverse an accounting entry once."
                ).format(move.display_name, move.reverse_entry_id.display_name)
            )
        reversed_move = move_env.search([("reverse_entry_id", "=", move.id)])
        if reversed_move:
            raise UserError(
                _(
                    "The accounting entry {} is the reversal of another entry ({}). "
                    "You can not reverse a reversal accounting entry."
                ).format(move.display_name, reversed_move.display_name)
            )
        return super().reverse_moves()
