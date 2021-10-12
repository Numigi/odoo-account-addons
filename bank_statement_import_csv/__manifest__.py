# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Bank Statement Import CSV",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com",
    "license": "AGPL-3",
    "category": "Accounting",
    "summary": "Import bank statement import from csv / xlsx files",
    "depends": [
        "account_bank_statement_import",
        "base_sparse_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_journal.xml",
        "views/bank_statement_import_config.xml",
        "wizard/bank_statement_import_wizard.xml",
    ],
    "installable": True,
}
