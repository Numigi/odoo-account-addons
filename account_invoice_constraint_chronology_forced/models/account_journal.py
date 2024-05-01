# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.onchange("type")
    def _onchange_type(self):
        super()._onchange_type()
        if self.type == "sale":
            self.check_chronology = True
        if self._origin.type == "sale":
            domain = [
                ("journal_id", "=", self._origin.id),
                ("move_type", "=", "out_invoice"),
            ]
            moves_count = self.env["account.move"].search_count(domain)
            if moves_count > 0:
                raise UserError(
                    _(
                        "You cannot change the Type of the Journal because there is "
                        "At Least One Account Move linked to the Journal."
                    )
                )

    @api.model
    def create(self, vals):
        if "type" in vals and vals.get("type") == "sale":
            vals["check_chronology"] = True
        return super().create(vals)

    def write(self, vals):
        if "type" in vals and vals.get("type") == "sale":
            vals["check_chronology"] = True
        return super().write(vals)
