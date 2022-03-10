# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Bank Statement Online Stripe",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com",
    "license": "AGPL-3",
    "category": "Accounting",
    "summary": "Online bank statement import for Stripe",
    "depends": [
        "account_bank_statement_import_online",
    ],
    "data": [
        "views/account_bank_statement_line.xml",
        "views/online_bank_statement_provider.xml",
    ],
    "installable": True,
}
