# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountReconciliationWidget(models.AbstractModel):

    _inherit = "account.reconciliation.widget"

    @api.model
    def _domain_move_lines_for_reconciliation(self, st_line, *args, **kwargs):
        domain = super()._domain_move_lines_for_reconciliation(st_line, *args, **kwargs)
        lines = self.env["account.move.line"].search(domain)
        included_lines = lines.filtered(
            lambda move_line: not _should_filter_line(st_line, move_line)
        )
        return [("id", "in", included_lines.ids)]


def _should_filter_line(st_line, move_line):
    is_liquidity = move_line.account_id.internal_type == "liquidity"

    if not is_liquidity and move_line.payment_id:
        return True

    if not is_liquidity and st_line.journal_id.reconcile_show_payments_only:
        return True
