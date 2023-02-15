# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    stripe_id = fields.Char(index=True)
    stripe_payload = fields.Text()
