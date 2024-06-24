# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Closing Journal",
    "version": "16.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Allow to define a fiscal year closing journal",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_move_line.xml",
    ],
    "installable": True,
}
