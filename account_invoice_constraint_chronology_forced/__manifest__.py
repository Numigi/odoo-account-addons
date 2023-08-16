# © 20123 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Invoice Constraint Chronology Forced',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add menu entries to configure bank accounts and banks of partners',
    'depends': [
        'account_invoice_constraint_chronology',
    ],
    "data": ["views/account_journal.xml"],
    'installable': True,
}
