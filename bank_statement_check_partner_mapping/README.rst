====================================
Bank Statement Check Partner Mapping
====================================

This module automates the generation of partner mapping rules for check payments and improves bank statement reconciliation.

.. image:: static/description/partner_mapping.png

When a check payment is posted and a check number is assigned, the module automatically generates a specific mapping rule for the partner. During bank statement reconciliation, these rules are used to accurately find the corresponding partner by matching the ``payment_ref`` or ``ref`` fields, ensuring strict isolation per bank journal.

Configuration
=============

To configure this module, you need to:

1. Go to **Accounting > Configuration > Accounting > Journals**.
2. Open a Bank journal.
3. Under the **Bank Account** tab, locate the **Check Partner Mapping Configuration** section.
4. Set your specific **Check Format on Statement** (e.g., ``CHK - {check_number}``).

Usage
=====

To use this module:

1. Create and post an outbound payment using the **Check** payment method.
2. Print the check or assign a check number.
3. The system will automatically create a mapping rule linking the partner, the journal, and the formatted check label.
4. If the payment is cancelled or reset to draft, the generated mapping rule will be automatically archived.
5. During Bank Statement Reconciliation, the system will accurately detect the partner based on the check number received from the bank, searching first in the statement line label, and falling back to the reference field.

Contributors
============

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.