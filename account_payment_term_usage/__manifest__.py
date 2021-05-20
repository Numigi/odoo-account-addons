# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Payment Term Usage',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Separate payment terms per usage.',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move.xml',
        'views/account_payment_term.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
