# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Aged Payables and Receivables in Foreign Currency",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "project",
    "depends": ["account_financial_report"],
    "summary": "Shows the original currency on receivable/payable account.",
    "data": [
        "report/templates/aged_partner_balance.xml",
    ],
    "installable": True,
}
