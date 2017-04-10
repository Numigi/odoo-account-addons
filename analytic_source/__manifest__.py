# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Analytic Source',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
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
