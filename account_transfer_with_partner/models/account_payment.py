# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_shared_move_line_vals(self, debit, credit, amount_currency,
                                   move_id, invoice_id=False):
        res = super(AccountPayment, self)._get_shared_move_line_vals(
            debit, credit, amount_currency, move_id, invoice_id=invoice_id)
        if self.payment_type == 'transfer':
            res['partner_id'] = self.company_id.partner_id.id
        return res
