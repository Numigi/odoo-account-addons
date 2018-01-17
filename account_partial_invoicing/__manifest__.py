# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partial invoicing",
    "summary": "Allow partial invoicing of Sale Order lines",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.savoirfairelinux.com",
    "author": "Savoir-faire Linux, ",
    "installable": True,
    "depends": [
        'sale'
    ],
    "license": "LGPL-3",
    "data": [
        'views/sale_make_invoice_advance_view.xml',
    ],
}
