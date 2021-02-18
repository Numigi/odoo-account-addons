# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.constrains("statement_line_id")
    def _check_statement_line_id__no_reverse(self):
        for line in self:
            if line.statement_line_id and line.move_id.reverse_entry_id:
                raise ValidationError(
                    _(
                        "The journal item {item} can not be reconciled in a bank statement. "
                        "It is reversed by {reversal_entry}."
                    ).format(
                        item=line.display_name,
                        reversal_entry=line.move_id.reverse_entry_id.display_name,
                    )
                )

            if line.statement_line_id and line.move_id.reversed_entry_id:
                raise ValidationError(
                    _(
                        "The journal item {item} can not be reconciled in a bank statement. "
                        "It is the reversal of {reversed_entry}."
                    ).format(
                        item=line.display_name,
                        reversed_entry=line.move_id.reversed_entry_id.display_name,
                    )
                )
