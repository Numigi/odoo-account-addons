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
        'payment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/email_template.xml',
        'data/payment_method.xml',
        'views/bank_account.xml',
        'views/eft.xml',
        'views/journal.xml',
        'views/payment_with_eft_smart_button.xml',
        'wizard/eft_confirmation.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'installable': True,
}
