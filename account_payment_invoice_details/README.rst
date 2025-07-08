Account Payment Invoice Details
==============================

This module enhances vendor payment records by providing detailed allocation information, showing exactly how much was allocated to each individual invoice when a payment covers multiple invoices.

Context & Problem
-----------------
In standard Odoo, when you make a vendor payment that covers multiple invoices, you can see the total payment amount and which invoices were paid, but you cannot easily see the breakdown of how much was allocated to each specific invoice. This information is stored in JSON format within the invoice records, making it difficult to access and display.

**Example scenario:**
- You make a $1,500 payment to a vendor
- This payment covers 3 invoices: $800, $400, and $300
- In standard Odoo, you see the payment amount and the 3 invoices, but not the individual allocation amounts

This module solves this problem by extracting and displaying the allocation details in a user-friendly format.


What's Added
------------
* New **Allocation Details** tab in vendor payment forms
* List view showing invoice number, allocated amount, and currency
* Automatic computation based on payment reconciliation data
* New model to store allocation details with proper relationships

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)