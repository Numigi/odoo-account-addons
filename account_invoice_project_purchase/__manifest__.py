# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Invoice Project Purchase",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Account",
    "depends": ["account", "project", "purchase", "hr_timesheet"],
    "data": [
        # views
        "views/account_invoice.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
