# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Main Module',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Install all addons required for testing.',
    'depends': [
        'l10n_generic_coa',  # Used for testing addons

        'account_analytic_required_forbidden',
        'account_bank_menu',
        'account_budget_balance',
        'account_fr_ca_labels',
        'account_manual_entry_restricted',
        'account_move_access',
        'account_move_chatter',
        'account_negative_debit_credit',
        'account_payment_cancel_group',
        'account_report_line_menu',
        'budget_analysis_account_move_line',
        'canada_bank_transfer',
        'hr_expense_tax_adjustment',
        'invoice_currency_validation',
        'invoice_fiscal_position_required',
        'invoice_refund_not_earlier',
        'invoice_write_access',
        'invoice_write_access_purchase',
        'invoice_write_access_sale',
        'vendor_invoice_full_list',
    ],
    'installable': True,
}
