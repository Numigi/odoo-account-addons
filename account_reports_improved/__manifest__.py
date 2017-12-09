# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Accounting Reports Improved',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Make accounting reports configuration more user friendly',
    'depends': [
        'account_reports',
    ],
    'data': [
        'views/account_financial_report_line.xml',
    ],
    'installable': True,
    'application': False,
}
