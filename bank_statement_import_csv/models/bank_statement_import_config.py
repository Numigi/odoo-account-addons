# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BankStatementImportConfig(models.Model):

    _name = "bank.statement.import.config"
    _description = "Bank Statement Import Config"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    first_row = fields.Integer(
        default=2, help="The position of the first transaction line in the file."
    )
    reversed_order = fields.Boolean(
        help="Check this box is the lines in the csv files are ordered "
        "starting with the latest transaction."
    )
    delimiter = fields.Char(default=",", required=True)
    quotechar = fields.Char()
    encoding = fields.Char(
        required=True,
        default="utf-8",
        help="The technical code of the file encoding. "
        "\n\nTypical values:\n - utf-8\n - cp1252\n - latin-1",
    )

    date_index = fields.Integer(required=True, default=0)
    date_format = fields.Char(required=True)

    description_index = fields.Integer(
        required=True,
        default=0,
        string="Label Index",
    )

    reference_enabled = fields.Boolean()
    reference_index = fields.Integer()

    withdraw_deposit_enabled = fields.Boolean()
    withdraw_index = fields.Integer()
    deposit_index = fields.Integer()

    amount_index = fields.Integer()

    balance_enabled = fields.Boolean()
    balance_index = fields.Integer()

    currency_index = fields.Integer()
    currency_amount_index = fields.Integer()
    currency_amount_enabled = fields.Boolean()

    def get_csv_loader_config(self):
        return {
            "first_row": self.first_row,
            "delimiter": self.delimiter or None,
            "quotechar": self.quotechar or None,
            "date": {
                "index": self.date_index,
                "format": self.date_format,
            },
            "description": {
                "index": self.description_index,
            },
            "reference": {
                "index": self.reference_index,
            }
            if self.reference_enabled
            else None,
            "withdraw": {
                "index": self.withdraw_index,
            }
            if self.withdraw_deposit_enabled
            else None,
            "deposit": {
                "index": self.deposit_index,
            }
            if self.withdraw_deposit_enabled
            else None,
            "amount": {
                "index": self.amount_index,
            }
            if not self.withdraw_deposit_enabled
            else None,
            "balance": {
                "index": self.balance_index,
            }
            if self.balance_enabled
            else None,
            "currency": {
                "index": self.currency_index,
            }
            if self.currency_amount_enabled
            else None,
            "currency_amount": {
                "index": self.currency_amount_index,
            }
            if self.currency_amount_enabled
            else None,
        }