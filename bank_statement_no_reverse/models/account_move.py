# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def is_reversed_move(self):
        self.ensure_one()
        return bool(self.reverse_entry_id)

    @api.multi
    def is_reversal_move(self):
        self.ensure_one()
        return bool(self.search_count([("reverse_entry_id", "=", self.id)]))
