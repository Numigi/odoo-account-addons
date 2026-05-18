# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

{
    "name": "Bank Statement Check Partner Mapping",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Automate partner mapping generation for check payments "
               "and improve bank statement reconciliation.",
    "depends": [
        "bank_statement_partner_mapping",
    ],
    "data": [
        "views/account_journal.xml",
        "views/bank_statement_partner_mapping.xml",
    ],
    "installable": True,
    "application": False,
}
