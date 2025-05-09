# Copyright 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Account(models.Model):

    _inherit = "account.account"

    manual_entry_group_ids = fields.Many2many(
        "res.groups",
        "account_manual_entry_group_rel",
        "account_id",
        "group_id",
        "Entry Restriction",
    )
