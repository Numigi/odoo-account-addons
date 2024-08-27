# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import fields, models


class Account(models.Model):

    _inherit = "account.account"

    account_type = fields.Selection(
        selection_add=[
            ("expense_interest", "Interest Expenses"),
            ("expense_one_time_expenses", "One-time Expenses"),
            ("expense_tax", "Tax Expenses"),
        ],
        ondelete={
            "expense_interest": lambda rec: rec._compute_account_type(),
            "expense_one_time_expenses": lambda rec: rec._compute_account_type(),
            "expense_tax": lambda rec: rec._compute_account_type(),
        },
    )


class AccountTemplate(models.Model):

    _inherit = "account.account.template"

    account_type = fields.Selection(
        selection_add=[
            ("expense_interest", "Interest Expenses"),
            ("expense_one_time_expenses", "One-time Expenses"),
            ("expense_tax", "Tax Expenses"),
        ],
    )
