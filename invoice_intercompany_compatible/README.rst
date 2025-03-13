Invoice Intercompany Compatible
===============================

.. contents:: Table of Contents

Context
-------

The module `account_invoice_inter_company <https://github.com/OCA/multi-company/tree/16.0/account_invoice_inter_company>`_ allows to automatically generate the matching invoice in another company for intercompany sales and purchases.

Bank Accounts
-------------
When a purchase invoice is generated from a company A, the matching sale invoice is generated on the company B.

Because of a missing ``onchange`` function, the bank account of company A (the buyer) is set on the sale invoice,
instead of the bank account of company B.

When validating the purchase invoice, you get a blocking error message:

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/invoice_intercompany_compatible/static/description/wrong_bank_account_error.png

The above case happens if the superuser (OdooBot) is linked to the company A.

Solution
~~~~~~~~
After installing this module :

*When a purchase invoice is generated from a company A (here as `CA Company`) :

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/invoice_intercompany_compatible/static/description/vendor_invoice_with_correct_bank_account.png

*The bank account of the selling company is properly set on the sale invoice :

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/invoice_intercompany_compatible/static/description/invoice_with_updated_bank_account.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
