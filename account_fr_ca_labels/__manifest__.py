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
        'account',
        'lang_fr_activated',
    ],
    'data': [
        'views/journal.xml',
    ],
    'post_init_hook': '_update_fr_ca_terms',
    'installable': True,
}
