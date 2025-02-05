Account Move Supplier Ref Check
===============================

This module modifies the duplicate vendor reference check to only validate based on `partner_id` and `partner_ref`, instead of the default three fields. 

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