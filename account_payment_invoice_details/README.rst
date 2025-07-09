Account Payment Invoice Details
==============================

This technical module provides a function to extract detailed payment allocation information 
for **vendor bills (supplier invoices)** for use in reports and other custom developments.

.. important::
   This module is specifically designed for **vendor bill payments** (supplier invoices) only.
   It uses the `reconciled_bill_ids` field which contains only vendor bills, not customer invoices.

Features
--------

* Provides `_get_account_payment_details()` function on payment records
* Extracts allocation amounts from `invoice_payments_widget` JSON field for vendor bills
* Returns structured data for report generation
* Pure technical module without UI components
* **Works exclusively with vendor bills (move_type='in_invoice')**

Usage
-----

Call the `_get_account_payment_details()` method on any **vendor payment** record to get allocation details:

.. code-block:: python

    # Only works with vendor payments (payment_type='outbound', partner_type='supplier')
    vendor_payment = self.env['account.payment'].browse(payment_id)
    details = vendor_payment._get_account_payment_details()
    # Returns: [
    #     {
    #         'invoice_id': 123,
    #         'invoice': 'BILL/2025/001',
    #         'amount': 1500.0,
    #         'currency_id': 'USD'
    #     },
    #     ...
    # ]

Contributors
------------

* Numigi (tm) and all its contributors (https://bit.ly/numigiens)