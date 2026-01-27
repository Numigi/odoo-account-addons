# Copyright 2026 Numigi(tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Financial Report Ageing Date',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    "website": "https://www.numigi.com",
    'category': 'Accounting',
    'summary': 'Adds an option to compute aged balance based on invoice date or due date',
    'depends': [
        'account_financial_report',
    ],
    'data': [
        'views/aged_partner_balance_wizard_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
