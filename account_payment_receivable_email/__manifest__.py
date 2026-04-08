# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Payment Receivable Email',
    'version': '14.0.1.3.0',
    'category': 'Accounting',
    'author': 'Numigi',
    "maintainer": "Numigi",
    "website": "https://numigi.com",
    'license': 'LGPL-3',
    'depends': [
        'account',
        'mail',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
