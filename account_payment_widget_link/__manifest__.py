# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

{
    'name': 'Account Payment Widget Link',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Make items clickable on the invoice payment widget',
    'depends': ['account'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/payment_widget.xml',
    ],
    'installable': True,
}
