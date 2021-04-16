# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Invoice Write Access / Sale',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Restrict the creation/update of customer invoices',
    'depends': [
        'invoice_write_access',
        'sale_management',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': True,
}
