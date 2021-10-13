# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Canada Bank Transfer",
    "version": "1.2.0",
    "author": "Savoir-faire Linux,Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Accounting",
    "depends": [
        "payment",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "security/res_groups.xml",
        "data/mail_template.xml",
        "data/account_payment_method.xml",
        "views/bank_account.xml",
        "views/eft.xml",
        "views/journal.xml",
        "views/payment_search_with_filter.xml",
        "views/payment_with_eft_smart_button.xml",
        "wizard/eft_confirmation.xml",
        "wizard/payment_notice_email.xml",
    ],
    "external_dependencies": {
        "python": ["unidecode"],
    },
    "installable": True,
}
