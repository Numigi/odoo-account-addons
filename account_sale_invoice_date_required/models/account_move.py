# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if move.is_sale_document(include_receipts=True) and not move.invoice_date:
                raise UserError(
                    _("The invoice/refund date is required to validate this document.")
                )
        return super(AccountMove, self).action_post()
