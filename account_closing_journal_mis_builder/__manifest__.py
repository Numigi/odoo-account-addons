# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Closing Journal / Mis Builder",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Binding between Account Closing Journal and Mis Builder",
    "depends": [
        "account_closing_journal",
        # OCA/mis-builder
        "mis_builder",
    ],
    "data": ["views/mis_report.xml",],
    "installable": True,
    "auto_install": True,
}
