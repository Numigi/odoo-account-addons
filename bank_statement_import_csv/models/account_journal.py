# Copyright 2024 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    statement_import_config_id = fields.Many2one(
        "bank.statement.import.config",
    )
