# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# Backported to v12 by Numigi (https://bit.ly/numigi-com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Mail Autosubscribe",
    "summary": "Automatically subscribe partners to their company's invoices",
    "version": "12.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich", "Numigi"],
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["mail_autosubscribe", "account"],
    "website": "https://github.com/Numigi/odoo-account-addons",
    "data": ["data/mail_autosubscribe.xml"],
    "auto_install": True,
}
