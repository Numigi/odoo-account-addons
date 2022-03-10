Account Closing Wizard
=======================

.. contents:: Table of Contents

Context
-------
The module ``account_closing_journal`` defines a simple mecanism to record closing journal entries.

Closing entries can be easily excluded from the ``Income Statement`` using a simple domain filter
``[('is_closing', '=', False)]``.

It does not define a mecanism to help generate these journal entries.

Usage
-----
I go to the form view of an account. I notice a new checkbox ``Default Retained Earnings Account``.

.. image:: static/description/account_form.png

This box can be checked for only one account per company.

If checked, this account is used as the main account for closing entries.

I go to ``Accounting / Accounting / Actions / Fiscal Year Closing``.

.. image:: static/description/wizard_menu.png

.. image:: static/description/wizard.png

I select the period to close and the closing journal to use.

.. image:: static/description/wizard_filled.png

Only a journal defined as ``Closing Journal`` can be selected.

I click on the ``Confirm`` button.

A new journal entry is opened.

.. image:: static/description/account_move.png

I notice that the entry has one line per expense and revenue account.

.. image:: static/description/account_move_lines.png

The counterpart is the default retained earnings account.

.. image:: static/description/account_move_earnings_account.png

I post the journal entry.

.. image:: static/description/account_move_posted.png

Running the Wizard Twice
------------------------
After posting the closing entry, if you have extra journal entries to post in the closed period,
you do not need to revert the closing entry.

You just need to execute the wizard a second time.
The previous closing entry will be considered when computing the new entry.

.. image:: static/description/new_account_move.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
