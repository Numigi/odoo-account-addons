===========================
Account Additional Settings
===========================

In Odoo Community, key accounting configurations are managed within the company form, 
which can be accessible to users with company management rights. 
This creates potential security risks, as critical accounting settings should not be modified 
frequently and should be restricted to specific users.

Centralized Configuration Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To improve security and prevent accidental modifications, this module moves key invoicing settings to a dedicated section in the accounting configuration menu. 
This change ensures better control over financial settings and reduces the risk of unauthorized changes.

Features
--------

Default Accounts
~~~~~~~~~~~~~~~~
A new section **Default Accounts** is introduced under the accounting configuration menu, 
allowing users to set default values for essential accounting fields without accessing the company form.

Some key fields included:
- Journal Suspense Account
- Stock Input Account
- Stock Output Account
- Transfer Account
- Stock Valuation Account

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/14.0/account_additional_settings/static/description/default_accounts.png

Fiscal Periods
~~~~~~~~~~~~~~
A dedicated section **Fiscal Periods** is also introduced to manage financial period settings more efficiently.

- Last Day
- Last Month

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/14.0/account_additional_settings/static/description/fiscal_periods.png

Community Version Only
----------------------
This module is designed to work exclusively on the **Community** version of Odoo. 
The **Enterprise** edition already includes this functionality natively.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
