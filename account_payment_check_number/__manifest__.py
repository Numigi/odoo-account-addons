# Copyright 2025 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': "Account Payment Check Number",
    'summary': """
        Adds the 'check_number' field to the supplier payment tree view and a search filter.
    """,
    'description': """
        This module inherits the supplier payment list view to add the 'check_number' column.
        It also adds a filter to search for payments that have a check number.
    """,
    'author': 'Numigi',
    'website': "https://numigi.com",
    'category': 'Accounting',
    'version': '1.0.0',
    'depends': ['account'],
    'data': [
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}