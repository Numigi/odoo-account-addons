# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    @api.model
    def _prepare_counterpart_move_lines_vals(self, *args, **kwargs):
        vals = super()._prepare_counterpart_move_lines_vals(*args, **kwargs)
        vals["partner_id"] = self.company_id.partner_id.id
        return vals
