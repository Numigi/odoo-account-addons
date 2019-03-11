# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Account Move Chatter',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Add chatter and tracking of activity on account moves.',
    'author': 'Numigi',
    'depends': [
        'account_accountant',
        'account',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'application': False,
    'license': 'LGPL-3',
}
