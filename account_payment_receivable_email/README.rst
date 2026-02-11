Account Payment Receivable Email
================================

TThis module allows users to define a specific email address for receivable accounts (payments) on the partner form.
Currently, Odoo sends payment receipts and notifications to the partner's main email address. With this module, you can specify a dedicated email in the 'Accounting' tab.

Features
--------

*New field 'Receivable Accounts Email' (payment_email) on the Partner form.

*Automatic use of this specific email when sending payment receipts or notifications.

*Fallback to the main partner email if the specific receivable email is not defined.


Usage
-----

CTo use this module:

*Go to Contacts and select a supplier.

*Open the Accounting tab.

*Fill in the field Receivable Accounts Email.

*When you send a payment receipt (individually or in batch), the system will automatically address the email to this specific address.

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.