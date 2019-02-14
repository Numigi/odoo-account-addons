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

        'account_negative_debit_credit',
        'canada_bank_transfer',
        'hr_expense_tax_adjustment',
        'invoice_currency_validation',
        'invoice_fiscal_position_required',
    ],
    'installable': True,
}
