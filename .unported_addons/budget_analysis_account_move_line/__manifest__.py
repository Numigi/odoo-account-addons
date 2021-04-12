# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Budget Analysis Account Move Lines',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Display the journal entries from the budget analysis report.',
    'depends': ['account_budget'],
    'data': [
        'views/assets.xml',
        'views/crossovered_budget_lines.xml',
    ],
    'installable': True,
}
