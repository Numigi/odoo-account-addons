# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def _reverse_move(self, date=None, journal_id=None, auto=False):
        for move in self:
            if move.is_reversed_move():
                raise UserError(
                    _(
                        "The accounting entry {} is already reversed (by entry {}). "
                        "You can only reverse an accounting entry once."
                    ).format(move.display_name, move.reverse_entry_id.display_name)
                )
            reversed_move = move.get_reversed_move()
            if reversed_move:
                raise UserError(
                    _(
                        "The accounting entry {} is the reversal of another entry "
                        "({}). You can not reverse a reversal accounting entry."
                    ).format(move.display_name, reversed_move.display_name)
                )
        return super()._reverse_move(date, journal_id, auto)

    @api.multi
    def is_reversed_move(self):
        self.ensure_one()
        return bool(self.reverse_entry_id)

    @api.multi
    def get_reversed_move(self):
        return self.search([("reverse_entry_id", "=", self.id)], limit=1)
