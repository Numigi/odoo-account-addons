# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Reconcile OCA Extended',
    'version': '16.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Fixes for Account Reconcile OCA',
    'depends': [
        'account_reconcile_oca',
    ],
    "data": [
        "views/account_bank_statement_line.xml"
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "account_reconcile_oca_extended/static/src/js/reconcile_controller.js"
        ],
    }
}
