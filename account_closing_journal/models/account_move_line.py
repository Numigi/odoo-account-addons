# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    is_closing = fields.Boolean(
        "Is Closing Item", related="journal_id.is_closing", store=True,
    )
