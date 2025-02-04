# Copyright 2017 Savoir-faire Linux
# Copyright 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Canada Bank Transfer",
    "version": "16.0.1.0.0",
    "author": "Savoir-faire Linux,Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": """
        Generates credit transfer files for transactions
        between bank accounts in Canada.
    """,
    "depends": [
        "payment",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "security/res_groups.xml",
        "data/mail_template_data.xml",
        "data/account_payment_method_data.xml",
        "views/res_bank_views.xml",
        "views/res_partner_bank_views.xml",
        "views/res_partner_views.xml",
        "views/account_eft_views.xml",
        "views/account_journal_views.xml",
        "views/account_payment_views.xml",
        "views/res_config_settings.xml",
        "wizard/account_eft_confirmation_wizard_views.xml",
        "wizard/mail_compose_message_views.xml",
    ],
    "external_dependencies": {
        "python": ["unidecode"],
    },
    "installable": True,
}
