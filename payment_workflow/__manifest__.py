# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Payment Workflow',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add new contact types.',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_payment.xml',
    ],
    'installable': False,
    'application': False,
}
