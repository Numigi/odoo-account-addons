# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self, invoice=False):
        user = self.env.user
        for record in self:
            is_reversal_move = bool(self.search([("reverse_entry_id", "=", record.id)]))
            is_auto_reverse_move = record.auto_reverse
            user_has_group_reverse_account_moves = user.has_group(
                "account_move_reversal_access.group_reverse_account_moves"
            )
            if is_reversal_move or is_auto_reverse_move:
                if not user_has_group_reverse_account_moves:
                    raise ValidationError(
                        _(
                            "You haven't access to reverse account entries. Please "
                            "contact your administrator or manager."
                        )
                    )
                journal_type = record.journal_id.type
                if journal_type in ("bank", "cash"):
                    raise ValidationError(
                        _(
                            "You can't reverse a move on bank or cash journal type. "
                            "Please use the cancel function."
                        )
                    )
        return super().post(invoice)
