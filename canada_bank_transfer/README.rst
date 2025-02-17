========================
Canada EFT Bank Transfer
========================
This module enables to generate credit transfer files for transactions between bank accounts in Canada.

.. contents:: Table of Contents

Configuration
-------------
As member of `Invoicing / Billing Administrator`, I go to the list view of journals (`Configuration / Journals`).

I open the form view of my bank journal.

In the `Outgoing Payments` tab, I see a that `EFT` can be selected as payment method.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_eft_selection.png

Once selected, a new section `EFT` appears bellow.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_eft_fields.png

This section contains 5 fields.

User Short Name
~~~~~~~~~~~~~~~
This is a short version of your company name.
It must be composed of maximum 15 alphanumeric caracters.

User Long Name
~~~~~~~~~~~~~~~
This is a long version of your company name.

User Number
~~~~~~~~~~~
This number is attributed by your bank to identify your company.
It is composed of 10 alphanumeric caracters.

Destination
~~~~~~~~~~~
Your bank will provide this number to you.
This is a technical value of 5 digits used in the EFT file.
It indicates the data processing center that will handle your tranfers.
The value depends on the bank and the location of your company.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_eft_fields_filled.png

Sequence
~~~~~~~~
Each journal (with EFT enabled)
has its own distinct sequence for the EFT.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_eft_sequence.png

This sequence number is used by the bank to identify your payment batch.

..

    In previous versions of the module, only one sequence was defined per company.

If you let the field empty, the system will automatically create it when saving the journal.

You may edit the next number of the sequence.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_sequence_form.png

Therefore, when generating a new EFT, this number will be used.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_with_file_sequence_number.png

Bank Account Configuration
--------------------------
Next, I go to the `Jounal Entries` tab.

This tab contains the information related to my company's bank account.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_bank_account_tab.png

In the field `Account Number`, I create a bank account.

I fill my bank account number. It is composed from 7 to 12 digits.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/bank_account_number.png

In the field `Bank`, I create a bank.

I fill the name of the bank and its institution number, then I click on `Save`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/bank_fields.png

Back in the form view of my bank account, I fill the transit (branch) then I click on `Save`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/bank_account_transit.png

The configuration of my journal is now complete, I click on `Save`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/journal_form_save.png

Preparing the Payments
----------------------
As member of `Invoicing / Billing`, I go to `Invoicing / Vendors / Payments`.
Then I click on `Create`.
I fill the partner and the payment amount. I check `EFT` as payment method.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/payment_form.png

I click on `Save`, then I click on `Confirm`.

The payment is now `Posted`. At this stage, it is ready to be selected for an EFT transfer.

Also, a new filter `Not Sent` is added in payments.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/payment_not_sent_filter.png

Preparing the EFT
-----------------
Once I have multiple EFT payments posted, I go back to the list of vendor payments.

I check both the `Posted`, `Not Sent` and `EFT` filters.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/vendor_payment_list_filtered.png

I select my payments and click on `Generate EFT` in the action menu.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/vendor_payment_list_generate_eft.png

A draft EFT is created.

For each payment, I select the recipient bank account.

If the bank account is not already defined for a given partner, I may create and edit a new one.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_bank_account_field.png

A recipient bank account required the same fields as my company's bank account.

* The account number (7 to 12 digits)
* The bank
* The transit/branch number (5 digits)

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/partner_bank_account_form.png

The bank must have an institution number (3 digits).

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/partner_bank_form.png

Once all the destination bank accounts are selected, I click on `Validate`.

An error message appears if one of my bank accounts is not properly filled.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_validate_error.png

I fix the account number, then I click again on `Validate`.

The EFT is now `Ready`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_validate_to_ready.png

EFT Approval
------------
The group `Approve EFT` allows to approve the EFT.
This group is intended for the financial director or controller of your company.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_approval_group.png

As member of `Approve EFT`, I go to the EFT form view (`Invoicing / Vendors / EFT`).

I verify that the payments are accurate.
If any payment seems odd, I can click on the line and dilldown to the invoices.

Then I click on `Approve`. The `EFT` is now approved.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_approved.png

Restriction on Canceling Payment
--------------------------------
Once I have payment with EFT linked to it, and the payment is in `POSTED` state,
I can not reste to draft the payment anymore. If I still try to cancel it, I get the following message:

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/reset_to_draft_payment_usererror.png

Generating The File
-------------------
The current step can be done by a member of the group `Invoicing / Billing`.
In the EFT form view, I click on `Generate File` and a new field `File` appears.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_generate_file_button.png

I click on the file name to download the file to my computer.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_file_open.png

Using The EFT File
------------------
Now, I go to my bank's web portal to upload the file.

Check with your bank's documentation on how to proceed for this step.

Confirm The EFT
---------------
Once the file is processed by your bank, you will get a confirmation whether the payments were transfered properly.
The whole file could be rejected by your bank for some reason.

Otherwise, even if the file was accepted by your bank, some payments may be rejected by the recipient bank and bounce back.
In such case, the module allows you to identify which payments were successfully transmitted to the recipient account
and which were not.

As member of the group `Invoicing / Billing`, I click on `Confirm Sending`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_confirm_sending.png

Let's suppose the payment of 1000.00$CAD to `Ready Mat` bounced back.

I uncheck the `Completed` box under `Ready Mat`. Then I click on `Validate`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_confirmation.png

Multiple changes were applied to the `EFT`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_done.png

(1) The EFT is now `Done`.

(2) The 2 succeeding payments are the ckeckbox `Sent` checked.
    The payment dates were updated to match the EFT date.

(3) The failed payment with checkbox `Sent` Unchecked can be corrected later and selected into another EFT batch.

(4) A new button `Send Payment Notices` appears.
    This button allows to notice the recipients by email.

Payment Notices
---------------
This is the last step in the workflow of an `EFT`.
It is optional because you may or may not want to notice your suppliers by email.

I click on `Send Payment Notices`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_send_payment_notices.png

I verify that the email message is properly set. Then, I click on `Send`.

.. image:: https://raw.githubusercontent.com/Numigi/odoo-account-addons/16.0/canada_bank_transfer/static/description/eft_payment_notices_sent.png

The payment notices are now sent.

Contributors
------------
* Savoir-faire Linux
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
