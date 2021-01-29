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
        "l10n_generic_coa",  # Used for testing addons
        "account_analytic_required_forbidden",
        "account_bank_menu",
        "account_budget_balance",
        "account_closing_journal",
        "account_closing_journal_mis_builder",
        "account_fr_ca_labels",
        "account_move_chatter",
        "account_negative_debit_credit",
        "account_payment_cancel_group",
        "account_payment_from_move_line",
        "account_payment_term_usage",
        "account_payment_term_usage_purchase",
        "account_payment_term_usage_sale",
        "account_payment_widget_link",
        "account_report_line_menu",
        "account_report_trial_balance",
        "account_show_full_features",
        "account_type_archive",
        "account_unaffected_earnings_disabled",
        "budget_analysis_account_move_line",
        "canada_account_types",
        "canada_bank_transfer",
        "hr_expense_tax_adjustment",
        "invoice_currency_validation",
        "invoice_fiscal_position_required",
        "invoice_mass_mailing_with_layout",
        "invoice_refund_not_earlier",
        "invoice_write_access",
        "invoice_write_access_purchase",
        "invoice_write_access_sale",
        "old_accounts",
        "vendor_invoice_full_list",
    ],
    "installable": True,
}
