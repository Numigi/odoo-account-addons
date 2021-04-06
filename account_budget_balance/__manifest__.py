# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Budget Balance',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add the balance amount to the budget lines',
    'depends': [
        'account_budget',
    ],
    'data': [
        'views/crossovered_budget.xml',
        'views/crossovered_budget_lines.xml',
    ],
    'installable': False,
}
