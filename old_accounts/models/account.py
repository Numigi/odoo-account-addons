# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class Account(models.Model):

    _inherit = "account.account"

    old_accounts = fields.Text(
        help="This field allows to list related account numbers from previous systems "
        "and notes related to these."
    )
