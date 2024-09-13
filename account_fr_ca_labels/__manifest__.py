# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Canada French Accounting Labels',
    'version': '16.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Sanitize the accounting terms for Canada French',
    'depends': [
        'base',

    ],
    'data': [
        'data/translate.term.fr_ca.csv',
        'security/ir.model.access.csv',
        #'views/journal.xml',
        'views/translate_term_fr_ca.xml',
    ],
    'installable': True,
    'auto-install': True,
}
