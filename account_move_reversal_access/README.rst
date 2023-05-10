Account Move Reversal Access
============================

This modules restricts access to the function of reversing Journal Entries and make it draft based on the security groups of the user and the type of journal.
Making a journal entry and invoice to draft are also based on journal type associated to it (sale or purchase).

- A new group is created Reverse Account Moves
- In case of reversal Journal Entries or auto reverse Journal Entries:

  + Users without this new group cannot reverse those Journal Entries

  .. image:: static/description/account_move_reversal_access_no_access.png

  + Users cannot reverse those Journal Entries if the reversal Journal Type is Bank or Cash

  .. image:: static/description/account_move_reversal_access_journal_type.png

  + As a user who can create an invoice, I view a sales invoice (or accounting document) with the status ``Posted``.
      I notice that the ``Reset to draft`` button is not available.
    And as a user who can create an invoice, I view an invoice (or accounting document) for purchases with the status ``Posted``.
      I notice that the ``Reset to draft`` button is not available.
    The constraint is added so that, on a Sales or Purchases journal, the ``Reset to draft`` button is systematically invisible, on the account.move form.
  
  .. image:: static/description/sale_invoice_without_reset_to_draft.png

  .. image:: static/description/purchase_invoice_without_reset_to_draft.png

  + As a user with access to create and modify an accounting document, and not being part of the ``Account Moves : Reverse and Modify`` group, I consult an accounting document from a Miscellaneous, Cash or Bank journal with the status ``Posted``.
    I notice that I don't have a ``Reset to draft`` button on the journal entry form.

  .. image:: static/description/journal_entry_without_reset_to_draft.png
  
  + As a user with access to create and modify an accounting document, and belonging to the group ``Account Moves : Reverse and Modify``, I consult an accounting document from a Miscellaneous, Cash or Bank journal with the status ``Posted``. 
    I notice that I see that ``Reset to draft`` button is available.
  
  .. image:: static/description/journal_entry_with_reset_to_draft.png

Configuration
-------------
No configuration required apart from module installation.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Komit (https://komit-consulting.com)

More information
----------------
* Meet us at https://bit.ly/numigi-com
