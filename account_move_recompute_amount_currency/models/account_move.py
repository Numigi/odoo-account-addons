# © 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency,
                                            company, date):
        res = super()._get_fields_onchange_subtotal_model(
            price_subtotal, move_type, currency, company, date)
        res['amount_currency'] = 0.0
        return res
