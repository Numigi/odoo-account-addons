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

.. note::
   The function iterates through `reconciled_bill_ids` which contains only vendor bills.
   Customer invoices are not included in this field and therefore not processed by this module.

Technical Details
-----------------

* **Extends:** `account.payment` model
* **Main function:** `_get_account_payment_details()`
* **Data source:** `invoice_payments_widget` JSON field on vendor bills
* **Scope:** Only processes `reconciled_bill_ids` (vendor bills only)
* **Return format:** List of dictionaries with the following keys:
  
  - `invoice_id`: ID of the vendor bill
  - `invoice`: Name/number of the vendor bill
  - `amount`: Allocated amount for this bill
  - `currency_id`: Currency name

The module parses the JSON data in `invoice_payments_widget` to find the payment entry
matching the current payment ID and extracts the allocated amount for each **vendor bill**.

**Important technical notes:**

* The function only iterates through `reconciled_bill_ids`, which contains vendor bills exclusively
* Customer invoices are handled through `reconciled_invoice_ids` (not processed by this module)
* Filters out zero allocations automatically
* Handles malformed JSON gracefully by returning 0.0 for invalid data

This function can be used in:
* Custom vendor payment reports
* Vendor payment data export modules
* Supplier payment analysis tools
* Other technical integrations involving vendor payments

Alternative Implementation Considerations
----------------------------------------

**Relational Field Approach**

The ideal solution would be to add a relational field to directly display the payment allocation 
details in Odoo views. However, this implementation would be complex because:

* The data is based on the computed field `reconciled_bill_ids`
* The allocation amounts are stored in JSON format within `invoice_payments_widget`
* Creating a proper relational field would require:
  
  - A new model to store allocation details
  - Complex synchronization logic with payment reconciliation
  - Additional overhead for data consistency

For this reason, the current functional approach using `_get_account_payment_details()` provides
a simpler and more maintainable solution for extracting this information programmatically.

Testing the Module
------------------

You can test this module using several approaches:

**1. Scheduled Action (Cron Job)**

Create a scheduled action to generate payment allocation reports:


**2. Custom Report**

Create a simple report to display the allocation details:

**3. Manual Testing via Shell**

Test directly in the Odoo Shell


Contributors
------------

* Numigi (tm) and all its contributors (https://bit.ly/numigiens)