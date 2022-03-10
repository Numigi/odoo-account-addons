# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.multi
    def _reverse_move(self, *args, **kwargs):
        for move in self:
            if move.reverse_entry_id:
                raise UserError(
                    _(
                        "The accounting entry {} is already reversed (by entry {}). "
                        "You can only reverse an accounting entry once."
                    ).format(move.display_name, move.reverse_entry_id.display_name)
                )
            if move.reversed_entry_id:
                raise UserError(
                    _(
                        "The accounting entry {} is the reversal of another entry "
                        "({}). You can not reverse a reversal accounting entry."
                    ).format(move.display_name, move.reversed_entry_id.display_name)
                )
        return super()._reverse_move(*args, **kwargs)
