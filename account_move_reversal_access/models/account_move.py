# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):

    _inherit = "account.move"

    def _post(self, soft=True):
        self._check_reversal_move()
        return super()._post(soft)

    def _check_reversal_move(self):
        for move in self:
            if move.reversed_entry_id:
                move._check_group_reverse_account_moves()
                move.reversed_entry_id._check_reversal_journal_type_access()

    def _check_reversal_journal_type_access(self):
        if self.journal_id.type in ("bank", "cash"):
            raise ValidationError(
                _(
                    "You can't reverse a move on bank or cash journal type. "
                    "Please use the cancel function."
                )
            )

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

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            # applied the restriction only if journal type is sale
            if move.journal_id.type in ["sale"]:
                move.show_reset_to_draft_button = False
            else:
                super()._compute_show_reset_to_draft_button()
