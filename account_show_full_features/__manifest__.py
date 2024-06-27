# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Show Full Accounting Features',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Show the accounting features hidden in Odoo community',
    'depends': [
        'account',
    ],
    'data': [
        'data/ir_ui_menu.xml',
        'data/res_groups.xml',
    ],
    'installable': True,
}
