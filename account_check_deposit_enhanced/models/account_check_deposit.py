# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    def _prepare_move_vals(self):
        vals = super()._prepare_move_vals()
        for line in vals["line_ids"]:
            if line[2]['debit'] > 0:
                line[2]['partner_id'] = self.company_id.partner_id.id
        return vals
