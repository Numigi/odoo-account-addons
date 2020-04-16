# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountType(models.Model):

    _inherit = "account.account.type"

    active = fields.Boolean(default=True)
