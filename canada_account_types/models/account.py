# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import fields, models


class Account(models.Model):

    _inherit = "account.account"

    account_type = fields.Selection(
        selection_add=[
            ('interest_expenses', 'Interest Expenses'),
            ('one_time_expenses', 'One-time Expenses'),
            ('tax_expenses', 'Tax Expenses'),
            ('asset_current', 'Other Current Assets'),
            ('asset_fixed', 'Immobilisations'),
            ('asset_non_current', 'Other Non-current Assets'),
            ('liability_current', 'Other Current Liabilities'),
            ('income', 'Revenues'),
            ('income_other', 'One-time Revenues'),
            ('expense_direct_cost', 'Direct Costs'),
            ('expense', 'Indirect Costs'),
        ],
        ondelete={
            'interest_expenses': lambda rec: rec._compute_account_type(),
            'one_time_expenses': lambda rec: rec._compute_account_type(),
            'tax_expenses': lambda rec: rec._compute_account_type(),
        }
    )


class AccountTemplate(models.Model):

    _inherit = "account.account.template"

    account_type = fields.Selection(
        selection_add=[
            ('interest_expenses', 'Interest Expenses'),
            ('one_time_expenses', 'One-time Expenses'),
            ('tax_expenses', 'Tax Expenses'),
            ('asset_current', 'Other Current Assets'),
            ('asset_fixed', 'Immobilisations'),
            ('asset_non_current', 'Other Non-current Assets'),
            ('liability_current', 'Other Current Liabilities'),
            ('income', 'Revenues'),
            ('income_other', 'One-time Revenues'),
            ('expense_direct_cost', 'Direct Costs'),
            ('expense', 'Indirect Costs'),
        ],
    )
