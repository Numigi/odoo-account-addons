# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import AccessError


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    def action_cancel(self):
        """Restrict the payment cancellation to a specific group.

        If the user is member of the given group, call the super
        method with sudo. This allows to bypass access rules on
        account move lines.

        The `Payment cancelled` message is posted to the chatter.
        track_visibility is not used because the super method is
        called with sudo (odoobot would appear in the chatter
        instead of the real user).
        """
        is_user_authorized = self.env.user.has_group(
            'account_payment_cancel_group.group_cancel_payments')

        if not is_user_authorized:
            raise AccessError(
                _('You are not authorized to cancel payments.')
            )

        result = super(AccountPayment, self.sudo()).action_cancel()

        for payment in self:
            payment.message_post(body=_('Payment cancelled'))

        return result
