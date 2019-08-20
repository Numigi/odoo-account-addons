# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Invoice Write Access',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Restrict the creation/update of invoices',
    'depends': [
        'account',
        'base_extended_security',
    ],
    'data': [
        'security/res_groups.xml',
    ],
    'installable': True,
}
