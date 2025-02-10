Account Move Supplier Ref Check
===============================

This module does a check to only validate account moves for suppliers based on `partner_id` (Partner) and `ref` (Reference),
instead of the default three fields : `partner_id` (Partner), `ref` (Reference) and `invoice_date` (Invoice/Bill Date).

It ensures that the system does not allow vendor bills with the same reference and partner, even if they have different invoice dates.

Configuration
-------------
No configuration required apart from module installation.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com