Invoice Currency Validation
===========================

This module adds validations on customer and supplier invoices.
It prevents the use of a payable/receivable account or journal that does not match the selected currency on the invoice.

Also, when changing the currency on the invoice, the journal is also changed on the invoice.
The selected journal is the first (in order of sequence) that matches the invoice type and the currency.

Contributors
------------
* David Dufresne (david.dufresne@savoirfairelinux.com)
* Yasmine El Mrini (yasmine.elmrini@savoirfairelinux.com)
