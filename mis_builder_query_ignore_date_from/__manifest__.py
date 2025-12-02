# Copyright 2025 Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "MIS Builder - Ignore Date From in Queries",
    "summary": "Allows MIS Report queries to ignore the start date and "
               "fetch all data up to the end date.",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/mis-builder",
    "author": "Numigi, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mis_builder",
    ],
    "data": [
        "views/mis_report_view.xml",
    ],
}
