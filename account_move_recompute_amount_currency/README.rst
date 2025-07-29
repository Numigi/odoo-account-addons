====================================
!!!!!!!!!   DEPRECATED NOW !!!!!!!!!
====================================

Account Move Recompute Amount Currency
======================================

Context
-------
In vanilla Odoo, _get_fields_onchange_subtotal_model method is used to recompute the values of 'amount_currency'.


Overview
--------
After installing this module, amount_currency will be null for exchange stock valuation moves generated from the invoice.

Limits 
------
It leads to prices and tax amounts being reset to zero during updates, preventing the user from confirming their invoice.

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.


