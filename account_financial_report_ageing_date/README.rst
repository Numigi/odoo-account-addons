============================================
Aged Partner Balance: Invoice Date Option
============================================

This module extends the **Aged Partner Balance** report from the OCA module
``account_financial_report`` to allow analyzing debts based on the **Invoice Date** instead of the default **Due Date**.

Features
========

* **Choice of Ageing Method:** Adds a radio button in the report wizard allowing
    the user to choose between:

    * **Due Date:** Standard behavior (Collection/Overdue analysis).
    * **Invoice Date:** New behavior (Financial/DSO analysis).

* **Excel Improvement:** Automatically activates **Autofilters** on the generated
    Excel export for easier data manipulation.

Usage
=====

1.  Go to **Invoicing/Accounting > Reports > Aged Partner Balance**.
2.  In the wizard, you will see a new field **Ageing Method**.
3.  Select **Invoice Date** to calculate age buckets (0-30, 30-60...) based on
    the transaction date.
4.  Print PDF or Export XLSX.

Technical Notes
===============

* This module overrides the SQL injection method ``_inject_line_values``
    in ``report_aged_partner_balance``.
* It dynamically replaces the SQL column ``rlo.date_due`` with ``rlo.date``
    when "Invoice Date" is selected.
* It depends on ``account_financial_report`` (OCA).

Authors
=======

* Numigi

Contributors
============
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
================
* Meet us at https://bit.ly/numigi-com