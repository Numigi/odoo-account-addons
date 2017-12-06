Accounting Reports Improved
===========================

Improvement of the module account_reports from Odoo Enterprise.
It adds more convenience for configuring the reports.

The selection labels on the field special_date_changer are changed in order
to make them more explicit about their respective behavior.

A selection field 'Formula Type' is added on the form of a report line.
It allows to select one of 2 types of formula:

Sum of Children Lines
---------------------
When selecting 'Sum of Children Lines', the formula field is filled automatically
using the codes of children lines. If one children line is added, removed or modified,
the formula of the parent line's formula is updated.

Sum of Account Categories
-------------------------
When selecting 'Sum of Children Lines', a new field 'Account Types' is shown to the user.
The report line's domain is automatically updated using the ids of the account types
filled by the user. The fields 'Formula' and 'Group By' are also filled.

When using this option, the user may also enter an account tag to filter the results.
This is mostly used for filtering move lines for the cash flow statement.

Contributors
------------
* David Dufresne (david.dufresne@savoirfairelinux.com)

More information
----------------
* Module developed and tested with Odoo version 10.0
* For questions, please contact our support services
(support@savoirfairelinux.com)
