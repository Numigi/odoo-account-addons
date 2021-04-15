Invoice Currency Validation
===========================
This module adds validations on customer and supplier invoices.
It prevents the use of a journal that does not match the selected currency on the invoice.

.. contents:: Table of Contents

Context
-------
In Odoo, when selecting a journal on an invoice, the currency is updated.
However, when selecting a currency on an invoice, the journal is not updated.

This means, for example, that an invoice in a foreign currency can be posted in a journal of the company currency.

Because the journal is hidden in the ``Other Info`` tab, and not visible for all users,
this makes errors hard to prevent.

Usage
-----
As member of the group ``Accounting / User``, I go to the form view of a vendor bill.

.. image:: static/description/invoice_form.png

I set the currency to ``EUR``.

I notice that the journal is set to a purchase journal in EUR.

.. image:: static/description/invoice_eur_journal.png

The selected journal is the first journal found (in order of sequence) matching the following criterias:

* Matching the invoice currency.
* Matching the invoice company.
* Mathing the type of invoice (``Sale`` versus ``Purchase``).

If no matching journal is found, the ``Journal`` field is emptied on the invoice.

Constraint on Journal
---------------------
If for some reason, a user is able to create an invoice in a journal which does not match the invoice currency,
a blocking error message will be raised.

Constraint on Account
---------------------
Until Odoo version 12.0, this module defined constraint on the payable/receivable account so that
the currency of this account matched the invoice currency.

Since Odoo version 13.0, the code of Odoo regarding invoices and journal entries has been drastically complexified.

The constraint on accounts made sense in v12 because you could easily select a specific account on the invoice.
Since version 13.0, you can not.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Yasmine El Mrini (yasmine.elmrini@savoirfairelinux.com)
