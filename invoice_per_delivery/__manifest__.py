# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Invoice per delivery",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Create invoice per delivary for some partners",
    "depends": ["stock_account", "sale_stock"],
    "data": [
        "views/account_move.xml",
        "views/res_partner.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
    "application": False,
}
