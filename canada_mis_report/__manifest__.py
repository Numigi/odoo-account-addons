# Copyright 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Canada MIS Builder Reports",
    "version": "16.0.1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Add MIS Builder Reports for Canada",
    "depends": [
        # Numigi/odoo-account-addons
        "canada_account_types",
        # OCA/mis-builder
        "mis_builder",
        # Numigi/odoo-base
        "lang_fr_activated",
        # Odoo/odoo
        "l10n_ca",
    ],
    "data": [
        "data/mis_report_style.xml",
        "data/mis_report.xml",
        "views/mis_report_views.xml",
    ],
    "installable": True,
}
