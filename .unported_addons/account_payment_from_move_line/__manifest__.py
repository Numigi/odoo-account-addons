# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Payment From Move Line',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Generate payment from receivable journal item',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_line.xml',
        'wizard/account_payment_from_move_line.xml',
    ],
    'installable': True,
}
