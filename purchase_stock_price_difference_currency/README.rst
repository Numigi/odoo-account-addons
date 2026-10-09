Purchase Stock Price Difference Currency
========================================

.. contents:: Table of Contents

Summary
-------
This module corrects the native price difference entry that Odoo generates on
vendor bills in foreign currency when that difference is in fact only a
**currency conversion artifact** and not a real difference between the ordered
price and the received (valued) price.

Context
-------

Issue With the Native Price Difference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In anglo-saxon accounting with real-time inventory valuation, when a vendor bill
is validated Odoo posts a price difference pair (``569000`` / ``226050``) just
before setting the bill to *Posted*.

When the purchase is made in a foreign currency, this native difference is
computed by reconverting the valuation layer at the exchange rate of the day the
reception was done. As a result, a difference appears even when the billed price
and the purchase order price are identical: the amount is purely an exchange rate
artifact, not a genuine price difference.

How This Module Fixes It
~~~~~~~~~~~~~~~~~~~~~~~~~~
The module ships a ``base.automation`` (automated action) triggered **on the
creation** of a journal item, applied on anglo-saxon lines of draft vendor bills
and refunds.

The action recomputes the difference from the **currency amount of the valuation
entry** (the purchase order price at reception) instead of the reconverted layer.

* If the recomputed difference is zero, the native price difference pair is
  removed (it was only an exchange artifact).
* Otherwise, the price difference unit price is corrected and Odoo recomputes the
  amounts.

The native reconciliation then does the rest (``ECH`` exchange entry on
``568010``). A message is posted on the bill documenting what was corrected.

Usage
-----
Once installed, the automated action runs transparently. No configuration is
required.

The automated action can be reviewed and (de)activated under
``Settings / Technical / Automation / Automated Actions``, with the name
``SRNF - Écart de prix sans artefact de change (ne pas archiver)``.

Each correction is traced in the bill's chatter.

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.
