# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Closing Wizard",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Add a wizard to close an accounting exercise",
    "depends": [
        "account_closing_journal",
        "date_range",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account.xml",
        "wizard/account_closing_wizard.xml",
    ],
    "installable": True,
}
