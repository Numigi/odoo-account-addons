# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BankStatementImportWizardLine(models.TransientModel):

    _name = "bank.statement.import.wizard.line"
    _description = "Bank Statement Import Wizard Line"

    wizard_id = fields.Many2one(
        "bank.statement.import.wizard", required=True, ondelete="cascade"
    )
    date = fields.Char()
    amount = fields.Char()
    currency = fields.Char()
    currency_amount = fields.Char()
    balance = fields.Char()
    description = fields.Char()
    reference = fields.Char()
    has_error = fields.Boolean()
