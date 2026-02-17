# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Account(models.Model):

    _inherit = "account.account"

    additional_group_id = fields.Many2one(
        "account.additional.group", index=True, ondelete="restrict"
    )
