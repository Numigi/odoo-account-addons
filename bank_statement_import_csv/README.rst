=========================
Bank Statement Import CSV
=========================

.. contents:: Table of Contents

Summary
-------
This module allows to import bank statement in CSV format,
without the headache that usually comes with it.

Context
-------

File Parameters
~~~~~~~~~~~~~~~
A common format of file available to export a bank statement in most banks is ``csv``.

A ``csv`` file relatively easy to parse as long as you have the correct parameters including:

* The encoding
* The field delimiter
* The quote char

Then, you need to convert each field into the correct data type.
Converting text into dates, numbers and currencies requires carefulness.

A known issue with bank statement files is that users manipulate the file
(with a non-developper software, typically Excel) before uploading it into the system.

Typically, they does so in order to remove extra content at the beginning of the file.

Doing so, the user (without aknowledging it) changes the parameters of the file,
sometimes making it non-readable by the system.

Field Mapping
~~~~~~~~~~~~~
When loading a csv file, you need to know which column appears where in the file.

One way of identifying the fields is to match the name of the columns.

Another way is to identify columns by their position.

Either way, no solution prevents the format to change over time,
thus making the mapping obsolete.

However, the position of columns is less likely to change over time
than the header labels.

Configuration
-------------
As member of ``Invoicing / Billing Administrator``, I go to
``Invoicing / Configuration / Accounting / Bank Statement Import Configurations``.

.. image:: static/description/import_config_menu.png

I click on ``Create``.

.. image:: static/description/import_config_form.png

I define the different parameters according to the csv format provided by my bank.

First Row
~~~~~~~~~
The ``First Row`` parameter defines the number of the line at which the first transaction appears.

Here is an example of file where the first row is ``3``.

.. image:: static/description/example_csv_first_row.png

Reversed Order
~~~~~~~~~~~~~~
Check this box if your transactions appear in backward order in your csv file.

This is mostly relevant if the csv file contains a balance column.
In such case, the first and last rows in the file are used to determine the
initial and ending balance.

Encoding
~~~~~~~~
The field ``Encoding`` must contain the technical value of the format in which the file is encoded.

Typical values include:

* utf-8
* latin-1
* cp1252

Delimiter
~~~~~~~~~
The field ``Delimiter`` must contain the character used to separate fields in the csv file.

Decimal Separator
~~~~~~~~~~~~~~~~~
The field ``Decimal Separator`` must contain the character used to separate the integer part from the decimal part of the decimal value.
By default is comma.

Quotechar
~~~~~~~~~
The field ``Quotechar`` must contain the character used as text delimiter.

Columns
~~~~~~~

Date
****
The date is a mandatory column in the csv file.

You must supply the number of the column and the format used to parse the date.

The format must be specified in `Python Syntax <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_.

The most common formats are:

* %d-%m-%Y
* %d/%m/%Y
* %m-%d-%Y
* %m/%d/%Y
* %Y-%m-%d
* %Y/%m/%d

Label
*****
The ``Label Column`` field is mandatory.

It is mapped to the field ``Label`` (name) of the bank statement line.

Reference
*********
The ``Reference`` field is optional.

It is mapped to the field ``Reference`` (ref) of the bank statement line.

Partner Name
************
It is possible to enter the ``Partner Name``.

.. image:: static/description/import_config_partner_name.png

The name of the partner does not allow to automatically fill the ``Partner`` field on
bank statement lines.

However, it allows to fill the field ``Partner Name`` on statement lines.
This field gives a hint when manually selecting the partner for a transaction.

By default, the column ``Partner Name`` is not displayed on bank statement lines.

See the module `bank_statement_extra_columns <https://github.com/Numigi/odoo-account-addons/tree/12.0/bank_statement_extra_columns>`_ to display this column.

Amounts
*******
The module supports either an amount displayed as a single column in the file,
or withdraws and deposits separated in two columns.

If ``Withdraw / Deposit`` is checked, you need to supply columns for both columns.

.. image:: static/description/import_config_withdraw_deposit.png

If ``Withdraw / Deposit`` is unchecked, you need to supply the number of the amount column.

.. image:: static/description/import_config_amount.png

Reversed Widthdraw / Deposit
****************************
It is possible that your bank proposes the CSV statements with negative amounts in the withdraw columns
and positive amounts in the deposit columns (or vice versa).

Also, it is possible to reverse the amounts contained in the withdraw and deposit columns.

.. image:: static/description/import_config_reversed_amounts.png

Balance
*******
Optionnaly, the module allows to parse a balance column, containing the balance
of the bank account after the transaction.

.. image:: static/description/import_config_balance.png

This column does not add any info to the bank statement line itself.

However, it allows to automatically fill the initial and ending balances of the bank statement.

Amount Foreign Currency
***********************
In case your bank statement contains transactions in multiple currencies,
you may parse two extra columns.

.. image:: static/description/import_config_amount_foreign_currency.png

The column ``Currency`` expects the code of the currency in which the transaction occured.

The column ``Currency Amount`` expects the original amount of the transaction in the foreign currency.

The module only maps these fields for transactions in a currency different from the company currency.

Journal
~~~~~~~
I go to the form view of my bank journal.

In the tab ``Bank Account``, I select my statement import configuration.

.. image:: static/description/journal_form.png

Usage
-----
I go to the invoicing dashboard and click on ``Import Statements``.

.. image:: static/description/accounting_dashboard.png

The import wizard is opened.

The configuration defined on my journal is prefilled.

.. image:: static/description/wizard.png

I upload my file and click on ``Load File``.

.. image:: static/description/wizard_load_file.png

..

    The extra step of clicking on a button after uploading the file is
    due to limitations in the Odoo framework.

After loading the file, the system shows a row in red, meaning that there
were errors parsing the row.

.. image:: static/description/wizard_loaded_red_rows.png

I can manually fix the data in the row in error.
When a row is corrected, I click on ``Validate``.

.. image:: static/description/wizard_row_validate.png

When all rows are corrected, the confirmation button appears in the bottom of the file.

.. image:: static/description/wizard_confirm.png

After clicking on the button, the new bank statement is displayed.

.. image:: static/description/bank_statement_form.png

I notice that the transaction lines where properly created.

I also notice that the initial and ending balances are properly set.
And, the name of the generated bank statement is the name of the imported file.

.. image:: static/description/bank_statement_with_name.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
