# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountType(models.Model):

    _inherit = "account.account.type"
    _order = "sequence"

    sequence = fields.Integer()
    active = fields.Boolean(default=True)
