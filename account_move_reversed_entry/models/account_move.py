# Copyright 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    reversed_entry_ids = fields.One2many(
        "account.move",
        "reversed_entry_id",
        "Reversed Entries",
    )

    reverse_entry_id = fields.Many2one(
        "account.move", compute="_compute_reversed_entry_id"
    )

    @api.depends("reversed_entry_ids")
    def _compute_reversed_entry_id(self):
        for move in self:
            move.reverse_entry_id = move.reversed_entry_ids[:1]

    def action_view_reversed_entries(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Reversed Entries",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.reversed_entry_ids.ids)],
        }
