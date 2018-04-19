# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Invoice Fiscal Position Required',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Make the fiscal position required on invoices.',
    'depends': ['account'],
    'data': [
        'views/account_invoice.xml',
    ],
    'installable': True,
}
