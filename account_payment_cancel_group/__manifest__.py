# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Payment Cancel Group",
    "version": "16.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Add a user group allowed to cancel payments",
    "depends": [
        "account",
    ],
    "data": [
        "security/res_groups.xml",
        "views/account_payment.xml",
    ],
    "installable": True,
}
