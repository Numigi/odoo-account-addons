# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Report Trial Balance",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Add a dynamic general ledger report",
    "depends": [
        "account",
    ],
    "data": [
        "report/report.xml",
        "views/account_report_trial_balance.xml",
    ],
    "qweb": ["static/src/xml/templates.xml"],
    "installable": True,
}
