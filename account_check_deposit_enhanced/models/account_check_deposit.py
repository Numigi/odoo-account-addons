# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountCheckDeposit(models.Model):

    _inherit = "account.check.deposit"

    @api.model
    def _prepare_counterpart_move_lines_vals(self, deposit, *args, **kwargs):
        vals = super()._prepare_counterpart_move_lines_vals(deposit, *args, **kwargs)
        vals ["partner_id"] = deposit.company_id.partner_id.id
        return vals
