# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: disable=pointless-statement
# noqa: B018

{
    "name": "Account Move Secure",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "summary": "Hides the closing_type field and restricts the Secure Entries menu.",
    "depends": ["account", "account_fiscal_year_closing"],
    "data": [
        "security/res_groups.xml",
        "views/account_move.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
}
