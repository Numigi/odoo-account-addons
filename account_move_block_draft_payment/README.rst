================================
Account Move Block Draft Payment
================================

.. contents:: Table of Contents

Context
-------
In standard Odoo, it is sometimes possible to trigger the payment registration
action on invoices that are still in a draft or cancelled state (for instance,
via the action menu or specific workflows). This behavior can lead to
inconsistencies in the accounting process, as payments should normally only
be registered against validated (posted) invoices.

Summary
-------
This module secures the invoicing process by strictly preventing users from
registering payments on unposted invoices.

Specifically, it overrides the payment registration action to enforce a strict
backend validation constraint. If a user attempts to register a payment for a
draft or cancelled invoice, a validation error is raised, stopping the process
immediately.

Usage
-----
To see this module in action:

1. Go to **Invoicing > Customers > Invoices**.
2. Open an existing draft invoice or create a new one.
3. Attempt to trigger the payment registration action.
4. The system will immediately raise a validation error:
   *"You cannot register a payment for an unposted invoice."*

The same strict restriction applies to cancelled invoices. Validated (posted)
invoices remain unaffected and proceed to the payment wizard as usual.

Bug Tracker
-----------
Bugs are tracked on the repository issues tracker. In case of trouble, please
check there if your issue has already been reported.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)