# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Bank Statement Status',
    'version': '16.0.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add Status field on account bank statement',
    'depends': [
        'account_statement_base',
    ],
    "data": [
        "views/account_bank_statement.xml"
    ],
    "installable": True,
}
