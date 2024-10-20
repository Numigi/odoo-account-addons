# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Reversal Access",
    "summary": """
        Restricting access to the function of reversing Journal
        Entries and resetting to draft ().
    """,
    "version": "14.0.2.0.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/res_groups.xml",
        "views/account_move.xml",
    ],
    "installable": True,
}
