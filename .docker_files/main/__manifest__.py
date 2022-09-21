# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Main Module",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Install all addons required for testing.",
    "depends": [
        "account_accountant", # Used for testing account_fr_ca_labels
        "l10n_generic_coa",  # Used for testing addons
        "account_additional_group",
        "account_analytic_required_forbidden",
        "account_bank_menu",
        "account_check_deposit_enhanced",
        "account_closing_journal",
        "account_closing_journal_mis_builder",
        "account_closing_wizard",
        "account_fr_ca_labels",
        "account_move_reversal_access",
        "account_move_unique_reversal",
        "account_negative_debit_credit",
        "account_payment_cancel_group",
        "account_payment_term_usage",
        "account_payment_term_usage_purchase",
        "account_payment_term_usage_sale",
        "account_payment_widget_link",
        "account_report_line_menu",
        "account_report_trial_balance",
        "account_show_full_features",
        "account_type_sane",
        "account_unaffected_earnings_disabled",
        "bank_statement_import_csv",
        "bank_statement_extra_columns",
        "bank_statement_no_reverse",
        "bank_statement_partner_name",
        "canada_account_types",
        "canada_bank_transfer",
        "invoice_currency_validation",
        "invoice_fiscal_position_required",
        "invoice_list_email",
        "invoice_refund_not_earlier",
        "lang_fr_activated",
        "old_accounts",
        "payment_list_not_sent",
    ],
    "installable": True,
}
