# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bank Statement Reconciliation Report",
    "summary": """
        Bank Statement Reconciliation Report
        """,
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "category": "Account",
    "version": "12.1.4",
    "depends": ["account_check_printing"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_bank_statement_views.xml",
        "report/account_bank_statement_report.xml",
        "wizard/conciliation_wizard_views.xml",
    ],
}
