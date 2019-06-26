# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import AccessError


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.multi
    def cancel(self):
        is_user_authorized = self.env.user.has_group(
            'account_payment_cancel_group.group_cancel_payments')

        if not is_user_authorized:
            raise AccessError(
                _('You are not authorized to cancel payments.')
            )

        result = super(AccountPayment, self.sudo()).cancel()

        for payment in self:
            payment.message_post(body=_('Payment cancelled'))

        return result
