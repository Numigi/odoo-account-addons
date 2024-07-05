# Copyright 2022 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


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
    quotechar = fields.Char(default='"')
    encoding = fields.Char(
        required=True,
        default="utf-8",
        help="The technical code of the file encoding. "
        "\n\nTypical values:\n - utf-8\n - cp1252\n - latin-1",
    )

    date_column = fields.Integer(required=True, default=0)
    date_format = fields.Char(required=True)

    description_column = fields.Integer(
        required=True,
        default=0,
        string="Label Column",
    )

    reference_enabled = fields.Boolean()
    reference_column = fields.Integer()

    partner_name_enabled = fields.Boolean()
    partner_name_column = fields.Integer()

    withdraw_deposit_enabled = fields.Boolean()
    withdraw_column = fields.Integer()
    reverse_withdraw = fields.Boolean(
        help="Check this box if the withdraw column contains negative amounts."
    )
    deposit_column = fields.Integer()
    reverse_deposit = fields.Boolean(
        help="Check this box if the deposit column contains negative amounts."
    )

    amount_column = fields.Integer()

    balance_enabled = fields.Boolean()
    balance_column = fields.Integer()

    currency_column = fields.Integer()
    currency_amount_column = fields.Integer()
    currency_amount_enabled = fields.Boolean()

    decimal_separator = fields.Char(
        required=True,
        default=",",
        help=(
            "The character used to separate the integer part "
            "from the decimal part of the decimal value. By default is comma."
        ),
    )
    thousands_separator = fields.Char(
        default=" ",
        help=(
            "The character used to separate the thousands in decimal value. "
            "By default is space."
        ),
        trim=False,
    )

    def get_csv_loader_config(self):
        return {
            "first_row_index": self.first_row - 1,
            "delimiter": self.delimiter or None,
            "quotechar": self.quotechar or None,
            "decimal_separator": self.decimal_separator,
            "thousands_separator": self.thousands_separator or "",
            "date": {
                "index": self.date_column - 1,
                "format": self.date_format,
            },
            "description": {
                "index": self.description_column - 1,
            },
            "reference": (
                {
                    "index": self.reference_column - 1,
                }
                if self.reference_enabled
                else None
            ),
            "partner_name": (
                {
                    "index": self.partner_name_column - 1,
                }
                if self.partner_name_enabled
                else None
            ),
            "withdraw": (
                {
                    "index": self.withdraw_column - 1,
                    "reverse": self.reverse_withdraw,
                }
                if self.withdraw_deposit_enabled
                else None
            ),
            "deposit": (
                {
                    "index": self.deposit_column - 1,
                    "reverse": self.reverse_deposit,
                }
                if self.withdraw_deposit_enabled
                else None
            ),
            "amount": (
                {
                    "index": self.amount_column - 1,
                }
                if not self.withdraw_deposit_enabled
                else None
            ),
            "balance": (
                {
                    "index": self.balance_column - 1,
                }
                if self.balance_enabled
                else None
            ),
            "currency": (
                {
                    "index": self.currency_column - 1,
                }
                if self.currency_amount_enabled
                else None
            ),
            "currency_amount": (
                {
                    "index": self.currency_amount_column - 1,
                }
                if self.currency_amount_enabled
                else None
            ),
        }
