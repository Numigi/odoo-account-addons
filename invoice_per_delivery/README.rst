Invoice Per Delivery
====================
This module provides the possibility to create an invoice per delivery order for specific partners.

.. contents:: Table of Contents

Usage
-----

From a contact form view, you can now check the checkbox Invoicing per delivery to generate an invoice for each delivery order of this client:

.. image:: static/description/invoicing_per_delivery_checkbox.png

- Check the `Invoicing per delivery` box in your client form view.
- Create a sales order with 2 storable products for your client.
- Confirm the sales order to generate the delivery order.
- In your delivery order, set the quantity done lower than the demand to generate a backorder delivery order for your sales order.

.. image:: static/description/delivery_order_form_view.png

- Validate your delivery order and then create a backorder for the remaining quantities. A smart button `Invoice` appears in the form view.

.. image:: static/description/delivery_order_invoice_button.png

- Click on the smart button to see the draft `Invoice` created from the delivery order.
- You can go to the delivery order that generated this Invoice through the smart button `Delivery`

.. image:: static/description/draft_invoice.png

- Go back to your sales order, then go to the backorder delivery and validate the backorder.
- You will see that a new Invoice is created for this backorder.

.. image:: static/description/backorder_invoice_button.png

.. image:: static/description/backorder_invoice.png

- Return to your sales order to see that the 2 Invoices are linked to it.

.. image:: static/description/sale_order_form_view.png

.. image:: static/description/sale_order_invoices.png



Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
