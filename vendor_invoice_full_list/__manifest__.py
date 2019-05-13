# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Vendor Invoice Full List',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Show refunds from Vendor Bills smart buttons',
    'depends': [
        'account',
        'purchase',
    ],
    'data': [
        'views/partner_smart_button.xml',
        'views/vendor_bill_amounts_signed.xml',
    ],
    'installable': True,
}
