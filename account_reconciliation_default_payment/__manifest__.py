# Copyright 2026 NUMIGI SOLUTIONS INC.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account Reconciliation Default Payment",
    "summary": "Change default tab in bank reconciliation widget",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "Numigi, Odoo Community Association (OCA)",
    "website": "https://github.com/Numigi/odoo-account-addons",
    "license": "LGPL-3",
    "depends": ["account_reconciliation_widget"],
    "data": [
        "views/assets.xml",
    ],
    "qweb": [
        "static/src/xml/reconciliation_line_override.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
