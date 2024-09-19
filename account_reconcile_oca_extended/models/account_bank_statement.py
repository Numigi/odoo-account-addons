# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models



class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def unlink(self):
        for statement in self:
            statement.line_ids.unlink()
        return super(AccountBankStatement, self).unlink()

    @api.depends("line_ids.internal_index", "line_ids.state")
    def _compute_date_index(self):
        for stmt in self:
            sorted_lines = stmt.line_ids.filtered(lambda line: line._origin.id).sorted(
                'internal_index')
            stmt.first_line_index = sorted_lines[:1].internal_index
            stmt.date = sorted_lines.filtered(lambda l: l.state == 'posted')[-1:].date

