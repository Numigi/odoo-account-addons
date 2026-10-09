# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Stock Price Difference Currency",
    "version": "14.0.1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Fix the native price difference that is only a currency artifact "
    "on vendor bills in foreign currency",
    "depends": [
        "base_automation",
        "purchase_stock",
        "stock_account",
    ],
    "data": [
        "data/base_automation.xml",
    ],
    "installable": True,
}
