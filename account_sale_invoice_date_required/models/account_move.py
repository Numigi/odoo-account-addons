# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, _

from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = 'account.move'

    def action_post(self):
        if not self.invoice_date:
            if self.is_sale_document(include_receipts=True):
                raise UserError(
                    _("The invoice date is required to validate this document.")
                )
        res = super(AccountMove, self).action_post()
        return res
