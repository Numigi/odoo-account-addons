# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice group by Parent Affiliate",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Account",
    "depends": ["account", "partner_affiliate_extended"],
    "summary": "Add the possibility to group by parent affiliate on invoices.",
    "data": [
        "views/account_move_views.xml",
    ],
    "installable": True,
}
