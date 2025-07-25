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
* Returns list of dictionaries with invoice objects and allocated amounts for report generation
* Pure technical module without UI components
* **Works exclusively with vendor bills (move_type='in_invoice')**

Usage
-----

Call the `_get_account_payment_details()` method on any **vendor payment** record to get allocation details:

.. code-block:: python

    # Only works with vendor payments (payment_type='outbound', partner_type='supplier')
    vendor_payment = self.env['account.payment'].browse(payment_id)
    payment_details = vendor_payment._get_account_payment_details()
    for detail in payment_details:
        invoice = detail['invoice']
        allocated_amount = detail['amount']
        print(f"Invoice: {invoice.name}, Allocated Amount: {allocated_amount}")
        # Result :
        # Invoice: BILL/2025/001, Allocated Amount: 100.00
        
        # You can also access all invoice properties:
        print(f"Invoice ID: {invoice.id}, Total: {invoice.amount_total}")


Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.