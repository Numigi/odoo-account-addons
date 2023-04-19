# © 2023 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Expense Tax Adjustment',
    'version': "14.0.1.0.0",
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Allow adjusting the tax amounts on expenses.',
    'depends': ['hr_expense', 'l10n_ca'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense.xml',
    ],
    'installable': True,
    'application': False,
}
