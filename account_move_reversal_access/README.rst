Account Move Reversal Access
============================

This modules restricts access to the function of reversing Journal Entries

- A new group is created Reverse Account Moves
- In case of reversal Journal Entries or auto reverse Journal Entries:

  + Users without this new group cannot reverse those Journal Entries

  .. image:: static/description/account_move_reversal_access_no_access.png

  + Users cannot reverse those Journal Entries if the reversal Journal Type is Bank or Cash

  .. image:: static/description/account_move_reversal_access_journal_type.png

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
