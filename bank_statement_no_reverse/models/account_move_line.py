# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self.check_bank_statement_no_reverse()
        return res

    @api.multi
    def check_bank_statement_no_reverse(self):
        to_check_moves = self.env["account.move"]
        for line in self.filtered(lambda r: r.statement_line_id):
            to_check_moves |= line.move_id
            if line.full_reconcile_id:
                reconciled_lines = line.full_reconcile_id.reconciled_line_ids
                for reconcile_move in reconciled_lines.mapped("move_id"):
                    to_check_moves |= reconcile_move
            for to_check_move in to_check_moves:
                if to_check_move.is_reversal_move() or to_check_move.is_reversed_move():
                    raise UserError(
                        _(
                            "The selected accounting entry is already reversed or is "
                            "the reversal of another entry. You must select another "
                            "line."
                        )
                    )
