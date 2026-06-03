# Copyright 2026 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Internal Transfer - Multi Currency",
    "version": "18.0.1.2.0",
    "author": "Numigi",
    "maintainer": "numigi",
    "website": "http://www.numigi.com",
    "category": "Accounting",
    "summary": "Handles multi-currency conversions for paired internal transfers.",
    "license": "LGPL-3",
    "depends": ["account_internal_transfer"],
    "data": [
        "views/account_payment_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
