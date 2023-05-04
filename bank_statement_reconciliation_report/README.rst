Bank statement reconciliation report
====================================
- Add smart button to model Account Bank Statement
- Print the bank conciliation report

Usage
-----------
- Install the module from Apps
- Go to Account Bank Statement, a smart button `Reconciliation Report` is added to the form view of the statement.

    .. image:: static/description/Reconciliation-Report-Smart-Button.png

- Click on the smart button, a popup will display with reconciliation information and a button `Print`.

    .. image:: static/description/Reconciliation-Report-Popup-Print-Button.png

- Click on `Print` button to print the report in PDF mode.

    .. image:: static/description/Bank-conciliation-Report-pdf.png

Details on calculation and conditions
-------------------------------------

All calculation of the following detail is based on the amount currency of the two tabs :

    .. image:: static/description/amount_currency_reconciliation_report_cheque.png
    .. image:: static/description/amount_currency_reconciliation_report_deposit.png

As a user who can edit a reconciliation report, when I edit a bank reconciliation report, for an accounting journal, whose associated accounting account has a currency different from the currency of the company, the calculation of the following fields is modified :

IMPORTANT !!!
Only if the company currency differs from the journal currency, values are computed as follows:

- The ``Total Outstanding Cheques`` field :
The calculation is based on the sum of the values ​​in the ``Amount Currency`` fields of the lines of the ``Outstanding cheques`` tab, multiplied by -1 to keep a positive total.

    .. image:: static/description/amount_curreny_to_total_outstanding_cheque.png

- The ``Total Outstanding Deposits`` field :
The calculation is based on the sum of the values ​​in the ``Amount Currency`` fields of the lines of the ``Outstanding Deposits`` tab.

    .. image:: static/description/amount_curreny_to_total_outstanding_deposit.png

- The ``Calculated Balance with Reconciliation`` field :
The field is calculated as follows: Statement Ending Balance - Total Outstanding Cheques (based on Amount Currency) + Total Outstanding Deposits (based on Amount Currency).

- The ``Balance at date field`` field :
The balance is calculated from the values ​​of the ``Amount Currency`` fields on the entries.

Configuration
-------------
No configuration required apart from module installation.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
