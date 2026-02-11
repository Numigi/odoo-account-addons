# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _notify_get_recipients(self, message, groups):
        """ Voir logique ci-dessus pour account.move """
        if self.partner_id.payment_email:
            return []
        return super(AccountPayment, self)._notify_get_recipients(message, groups)