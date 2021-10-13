========================
Canada EFT Bank Transfer
========================
This module enables to generate credit transfer files for transactions between bank accounts in Canada.

.. contents:: Table of Contents

Configuration
-------------
As member of `Accounting / Manager`, I go to the list view of accounting journals.

.. image:: static/description/journal_list.png

I open the form view of my bank journal.

In the 'Advanced Settings' tab, I see a checkbox `EFT`.

.. image:: static/description/journal_form_eft_checkbox.png

Once checked, a new section `EFT` appears bellow.

.. image:: static/description/journal_form_eft_fields.png

This section contains 3 fields.

User Short Name
~~~~~~~~~~~~~~~
This is a short version of your company name.
It must be composed of maximum 15 alphanumeric caracters.

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

.. image:: static/description/journal_form_eft_fields_filled.png

Sequence
~~~~~~~~
Since version ``1.2.0`` of the module, each journal (with EFT enabled)
has its own distinct sequence for the EFT.

.. image:: static/description/journal_form_eft_sequence.png

This sequence number is used by the bank to identify your payment batch.

..

    In previous versions of the module, only one sequence was defined per company.

If you let the field empty, the system will automatically create it when saving the journal.

You may edit the next number of the sequence.

.. image:: static/description/eft_sequence_form.png

Therefore, when generating a new EFT, this number will be used.

.. image:: static/description/eft_with_file_sequence_number.png

Bank Account Configuration
--------------------------
Next, I go to the `Bank Account` tab.

This tab contains the information related to my company's bank account.

.. image:: static/description/journal_form_bank_account_tab.png

In the field `Bank Account`, I click on "Create and Edit".

.. image:: static/description/journal_form_bank_account_field.png

I fill my bank account number. It is composed from 7 to 12 digits.

.. image:: static/description/bank_account_number.png

In the field `Bank`, I click on "Create and Edit".

.. image:: static/description/bank_account_bank_field.png

I fill the name of the bank and its institution number, then I click on `Save`.

.. image:: static/description/bank_fields.png

Back in the form view of my bank account, I fill the transit (branch) then I click on `Save`.

.. image:: static/description/bank_account_transit.png

The configuration of my journal is now complete, I click on `Save`.

.. image:: static/description/journal_form_save.png

Preparing the Payments
----------------------
As member of `Accounting / Billing`, I go to `Accounting / Vendors / Payments`.
Then I click on `Create`.

.. image:: static/description/vendor_payment_list.png

I fill the partner and the payment amount. I check `EFT` as payment method.

.. image:: static/description/payment_form.png

I click on `Save`, then I click on `Confirm`.

.. image:: static/description/payment_form_confirm.png

The payment is now `Posted`. At this stage, it is ready to be selected for an EFT transfer.

.. image:: static/description/payment_form_posted.png

Preparing the EFT
-----------------
Once I have multiple EFT payments posted, I go back to the list of vendor payments.

I check both the `Posted` and `EFT` filters.

.. image:: static/description/vendor_payment_list_filtered.png

I select my payments and click on `Generate EFT` in the action menu.

.. image:: static/description/vendor_payment_list_generate_eft.png

A draft EFT is created.

.. image:: static/description/eft_draft.png

For each payment, I select the recipient bank account.

If the bank account is not already defined for a given partner, I may create and edit a new one.

.. image:: static/description/eft_bank_account_field.png

A recipient bank account required the same fields as my company's bank account.

* The account number (7 to 12 digits)
* The bank
* The transit/branch number (5 digits)

.. image:: static/description/partner_bank_account_form.png

The bank must have an institution number (3 digits).

.. image:: static/description/partner_bank_form.png

Once all the destination bank accounts are selected, I click on `Validate`.

.. image:: static/description/eft_validate.png

An error message appears. One of my bank accounts is not properly filled.

.. image:: static/description/eft_validate_error.png

I fix the account number, then I click again on `Validate`.

.. image:: static/description/eft_fixed_validate.png

The EFT is now `Ready`.

.. image:: static/description/eft_ready.png

EFT Approval
------------
The group `Approve EFT` allows to approve the EFT.
This group is intended for the financial director or controller of your company.

.. image:: static/description/eft_approval_group.png

As member of `Approve EFT`, I go to the EFT form view.

.. image:: static/description/eft_list.png

I verify that the payments are accurate.
If any payment seems odd, I can click on the line and dilldown to the invoices.

Then I click on `Approve`.

.. image:: static/description/eft_approve.png

The `EFT` is now approved.

.. image:: static/description/eft_approved.png

Generating The File
-------------------
The current step can be done by a member of the group `Accounting / Billing`.

.. image:: static/description/eft_generate_file_button.png

A new field `File` appears.

.. image:: static/description/eft_file_generated.png

I click on the file name to download the file to my computer.

.. image:: static/description/eft_file_open.png

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

As member of the group `Accounting / Billing`, I click on `Confirm Sending`.

.. image:: static/description/eft_confirm_sending.png

Let's suppose the payment of 1000.00$CAD to `Ready Mat` bounced back.

I uncheck the `Completed` box under `Ready Mat`. Then I click on `Validate`.

.. image:: static/description/eft_confirmation.png

Multiple changes were applied to the `EFT`.

.. image:: static/description/eft_done.png

(1) The EFT is now `Done`.

(2) The 2 succeeding payments are at the status `Sent`.
    The payment dates were updated to match the EFT date.

(3) The failed payment is still at the status `Posted`.
    This payment can be corrected later and selected into another EFT batch.

(4) A new button `Send Payment Notices` appears.
    This button allows to notice the recipients by email.

Payment Notices
---------------
This is the last step in the workflow of an `EFT`.
It is optional because you may or may not want to notice your suppliers by email.

I click on `Send Payment Notices`.

.. image:: static/description/eft_send_payment_notices.png

I verify that the email message is properly set. Then, I click on `Send`.

.. image:: static/description/eft_payment_notices_sent.png

The payment notices are now sent.

Contributors
------------
* Savoir-faire Linux
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
