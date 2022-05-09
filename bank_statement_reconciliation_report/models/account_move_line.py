# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    rec_outbound_id = fields.Many2one("reconciliation.wizard")
    rec_inbound_id = fields.Many2one("reconciliation.wizard")
    state = fields.Selection(
        [("draft", "Unposted"), ("posted", "Posted")],
        string="Status",
        related="move_id.state",
    )
