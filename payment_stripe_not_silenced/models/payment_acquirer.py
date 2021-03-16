# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    def _stripe_request(self, url, data=False, method="POST"):
        self = self.with_context(stripe_manual_payment=True)
        return super(PaymentAcquirer, self)._stripe_request(url, data, method)
