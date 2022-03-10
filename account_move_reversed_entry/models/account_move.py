# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    reversed_entry_ids = fields.One2many(
        "account.move",
        "reverse_entry_id",
        "Reversed Entries",
    )

    reversed_entry_id = fields.Many2one("account.move", compute="_compute_reversed_entry_id")

    @api.depends("reversed_entry_ids")
    def _compute_reversed_entry_id(self):
        for move in self:
            move.reversed_entry_id = move.reversed_entry_ids[:1]
