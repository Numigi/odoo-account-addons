# Copyright 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency,
                                            company, date):
        res = super()._get_fields_onchange_subtotal_model(
            price_subtotal, move_type, currency, company, date
        )
        excluded_keys = {
            "recursive_onchanges",
            "append_type_to_tax_name",
            "skip_account_move_synchronization",
            "line_ids",
        }
        if self.move_id.invoice_line_ids and not any(
                key in self._context for key in excluded_keys):
            res["amount_currency"] = 0.0
        return res
