# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Analytic Source',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add field source to analytic lines.',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_analytic_line.xml',
    ],
    'installable': True,
    'application': False,
}
