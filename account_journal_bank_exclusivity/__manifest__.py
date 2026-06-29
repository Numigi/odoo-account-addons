# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: disable=pointless-statement
# noqa: B018

{
    "name": "Account Journal Bank Exclusivity",
    "summary": """
        Guarantees uniqueness and exclusivity of bank journal accounts.
    """,
    "version": "18.0.1.1.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["account_reconcile_oca"],
    "data": [],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
