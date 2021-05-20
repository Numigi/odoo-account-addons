# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """Allow to make the destination (counterpart) account explicit.

        In vanilla implementations of payments, the counterpart account is
        deduced from either the invoices to pay or the partner selected on the payment.

        In the case of this module, when opening the wizard, we already know
        against which counterpart account the payment must registered.
        This is the account of the selected journal items (account.move.line).

        Therefore, when posting the payment from the new wizard, the counterpart account
        is forced to the expected value.
        """
        forced_account_id = self._context.get('force_payment_destination_account_id')
        if forced_account_id:
            self.destination_account_id = self.env['account.account'].browse(forced_account_id)
        else:
            super()._compute_destination_account_id()
