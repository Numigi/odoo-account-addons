Account Reconciliation Default Payment
======================================
This module modifies the bank reconciliation widget to change the default behavior when reconciling bank statements. It renames the "Miscellaneous Matching" tab to "Outstanding payments" and sets it as the first and default active tab.

.. contents:: Table of Contents

Usage
-----
As a member of ``Accounting / Billing``, I go to the Accounting dashboard.

I click on the **Reconcile** button of a bank journal.

.. image:: static/description/dashboard_reconcile_button.png

In the bank reconciliation widget, I notice that the first tab is now named **Outstanding payments**.

.. image:: static/description/outstanding_payments_tab.png

This tab is selected and active by default when opening a reconciliation line. This prevents the accidental creation of duplicate payments when manual payments (outstanding payments) already exist in the system.

The **Customer/Vendor Matching** tab is now located in the second position.

.. image:: static/description/customer_vendor_matching_tab.png

You can still click on the second tab to match the statement with existing lines on receivable or payable accounts if needed.

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.