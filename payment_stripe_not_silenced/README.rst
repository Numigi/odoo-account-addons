Payment Stripe Not Slienced
===========================

Context
-------
As of Odoo 14.0, when an error happens in a request to stripe,
the error is silenced by default.

.. image:: static/description/odoo_source_code.png

This makes the errors caused by the stripe module very hard to diagnose.

Overview
--------
When this module is installed, the errors caused by the Stripe API are not silenced.

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.


