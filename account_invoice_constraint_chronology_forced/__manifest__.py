# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Constraint Chronology Forced",
    "version": "1.1.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "AGPL-3",
    "category": "Accounting",
    "summary": "Add menu entries to configure bank accounts and banks of partners",
    "depends": [
        "account_invoice_constraint_chronology",
    ],
    "data": ["views/account_journal.xml"],
    "installable": True,
    "post_init_hook": "sale_journals_check_chronology",
}
