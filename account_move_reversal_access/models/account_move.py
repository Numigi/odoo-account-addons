# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def write(self, vals):
        for move in self:
            if move.state == "posted" and vals.get("auto_reverse"):
                self._check_group_reverse_account_moves()
                self._check_reversal_journal_type_access(move.journal_id)
        return super().write(vals)

    @api.multi
    def post(self, invoice=False):
        self._check_reversal_move()
        self._check_auto_reverse_move()
        return super().post(invoice)

    @api.multi
    def _check_reversal_move(self):
        for move in self:
            being_reversed_move = self.search([("reverse_entry_id", "=", move.id)])
            is_reversal_move = bool(being_reversed_move)
            if is_reversal_move:
                move._check_group_reverse_account_moves()
                journal = being_reversed_move.journal_id
                move._check_reversal_journal_type_access(journal)

    @api.multi
    def _check_auto_reverse_move(self):
        for move in self.filtered(lambda m: m.auto_reverse):
            move._check_group_reverse_account_moves()
            move._check_reversal_journal_type_access(move.journal_id)

    @api.model
    def _check_reversal_journal_type_access(self, journal):
        if journal.type in ("bank", "cash"):
            raise ValidationError(
                _(
                    "You can't reverse a move on bank or cash journal type. "
                    "Please use the cancel function."
                )
            )

    @api.model
    def _check_group_reverse_account_moves(self):
        if not self.env.user.has_group(
            "account_move_reversal_access.group_reverse_account_moves"
        ):
            raise ValidationError(
                _(
                    "You haven't access to reverse account entries. Please "
                    "contact your administrator or manager."
                )
            )
