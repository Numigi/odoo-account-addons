# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BudgetLine(models.Model):

    _inherit = 'crossovered.budget.lines'

    def _get_move_line_domain(self):
        """Get the domain to filter the list view of journal items."""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]

        if self.general_budget_id:
            domain.append(('account_id', 'in', self.general_budget_id.account_ids.ids))

        if self.analytic_account_id:
            domain.append(('analytic_account_id', '=', self.analytic_account_id.id))

        return domain

    def action_view_move_lines(self):
        action = self.env.ref(
            'budget_analysis_account_move_line.action_move_lines_from_budget_lines')
        result = action.read()[0]
        result['display_name'] = '{} ({})'.format(result['name'], self.display_name)
        result['domain'] = self._get_move_line_domain()
        return result
