# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):

    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        for move in self:
            if move.statement_line_id:
                raise ValidationError(
                    _(
                        "The journal item {item} can not be reversed. "
                        "It is bound to a bank statement line ({statement_line})."
                    ).format(
                        item=move.display_name,
                        statement_line=move.statement_line_id.display_name,
                    )
                )

        return super()._reverse_moves(default_values_list, cancel)
