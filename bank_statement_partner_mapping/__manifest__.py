# © 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Bank Statement Partner Mapping",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Invoicing Management",
    "summary": "Mapping of partners on bank statements.",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/bank_statement_partner_mapping_views.xml",
        "views/account_bank_statement_views.xml",
    ],
    "installable": True,
}
