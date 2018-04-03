Negative Debit/Credit
=====================
In accounting, the following logic is often repeated:

* If my invoice line is positive, put the amount in the debit column.
* Otherwise, put the inverse amount in the credit column.

The Problem
-----------
The problem with that logic is that it is repeated almost everywhere an accounting entry is created
(invoicing, payments, expenses, payroll, etc.).

When an exception is raised because of a comparison error, the message is very nonspeaking to the user
and very hard to debug for the developper.

The Solution
------------
What the system could do instead is the following:

* Put the amount in the debit column.

Then, in a lower layer of code, the system would apply the following logic:

* If the debit is negative, put the inverse amount in the credit column.
* If the credit is negative, put the inverse amount in the credit column.

This is what this module does. It replaces the debit/credit amounts in the appropriate column
when creating accounting entries.

Contributors
------------
* David Dufresne <david.dufresne@numigi.com>
