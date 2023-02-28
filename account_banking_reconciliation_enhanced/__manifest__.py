# © 2023 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Banking Reconciliation enhanced',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Enhance the bank statement detail report and the bank statement summary report.',
    'depends': [
        'account_banking_reconciliation',
    ],
    'data': [
        'report/report_bank_statement_detail.xml',
        'report/report_bank_statement_summary.xml',

    ],
    'installable': True,
}
