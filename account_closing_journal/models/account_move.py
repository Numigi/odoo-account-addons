# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    is_closing = fields.Boolean(
        "Is Closing Entry",
        related="journal_id.is_closing",
        store=True,
    )
