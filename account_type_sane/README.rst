Account Type Sane
=================

.. contents:: Table of Contents

Context
-------
Odoo comes with the notion of a ``Type of Account``.

.. image:: static/description/vanilla_odoo_account_type.png

There are a few issues with this referential:

1. There is no menu to edit the list of account types.
2. The selector widget on accounts is misleading.
3. There is no sequence on account types.

Account Types
-------------
When this module is installed, a new menu entry is added to edit types of accounts.

.. image:: static/description/account_type_menu.png

I notice that the list view contains a sequence handle.

.. image:: static/description/account_type_sequence.png

I can open the form view to edit an account type.

.. image:: static/description/account_type_form.png

Accounts
--------
On accounts, I notice that the account type field is a standard manyone selector.

.. image:: static/description/account_field.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
