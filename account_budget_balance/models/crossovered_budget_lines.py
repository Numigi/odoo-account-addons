# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CrossoveredBudgetLines(models.Model):

    _inherit = "crossovered.budget.lines"

    balance = fields.Monetary(
        compute="_compute_balance_amount",
        string="Balance",
        help="The balance amount is equal to the planned amount "
        "minus the practical amount."
    )

    @api.depends('planned_amount', 'practical_amount')
    def _compute_balance_amount(self):
        for line in self:
            line.balance = line.planned_amount - line.practical_amount

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Allow reading the balance amount with group read.

        This is inspired by what is done in the module account_budget with the fields
        practical_amount, theoritical_amount and percentage.
        """
        result = super().read_group(
            domain, fields, groupby,
            offset=offset, limit=limit, orderby=orderby, lazy=lazy
        )
        if 'balance' in fields:
            for group_line in result:
                group_domain = group_line.get('__domain') or domain
                lines_that_compose_group = self.search(group_domain)
                group_line['balance'] = sum(lines_that_compose_group.mapped('balance'))

        return result
