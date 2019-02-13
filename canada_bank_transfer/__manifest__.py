# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Canada Bank Transfer',
    'version': '1.0.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'depends': [
        'account',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/payment_method.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'installable': True,
}
