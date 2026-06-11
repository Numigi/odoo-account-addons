# Copyright Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Main Module",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Install all addons required for testing.",
    "depends": [
        "account_additional_group",
        "account_bank_menu",
        "account_fiscalyear_end_on_company",
        "account_fr_ca_labels",
        "account_internal_transfer_multi_currency",
        "account_move_reversal_access",
        "account_move_unique_reversal",
        "account_payment_cancel_group",
        "canada_account_types",
        "canada_mis_report",
        "invoice_refund_not_earlier",
    ],
    "installable": True,
}
