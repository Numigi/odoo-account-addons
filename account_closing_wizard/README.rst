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

Blocking from closing fiscal year
---------------------------------
As a user using the Numigi account closing wizard, I have a blocking error message preventing me from closing my fiscal year if an accounting document with draft status is recorded in my company with a date equal to or prior to the end date of the fiscal year to be closed.

I have an unposted journal entry with a selected date and then I go to the menu to close a fiscal year.

.. image:: static/description/account_move_unposted.png

I have an end date that is superior to the unposted journal entry.

.. image:: static/description/closing_fiscal_year.png

I see an error preventing me to close the fiscal year.

.. image:: static/description/closing_fiscal_year_denied.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
