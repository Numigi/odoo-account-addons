# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Canada French Accounting Labels',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Sanitize the accounting terms for Canada French',
    'depends': [
        'account',
        'base_xml_rename',
        'lang_fr_activated',
    ],
    'data': [
        'views/journal.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
