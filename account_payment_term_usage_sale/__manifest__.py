# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Payment Term Usage Sale',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Filter payment terms on sale orders.',
    'depends': [
        'account_payment_term_usage',
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': True,
}
