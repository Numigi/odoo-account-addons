# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Additional Group",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Add additional groups of accounts",
    "depends": ["account",],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account.xml",
        "views/account_additional_group.xml",
    ],
    "installable": True,
}
