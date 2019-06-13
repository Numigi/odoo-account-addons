# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BudgetLine(models.Model):

    _inherit = 'crossovered.budget.lines'

    def get_practical_amount_move_line_ids(self):
        pass
