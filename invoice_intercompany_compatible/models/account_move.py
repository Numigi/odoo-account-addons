# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("company_id")
    def _onchange_company_set_partner_bank(self):
        if self.company_id and self.move_type in ("out_invoice", "in_refund"):
            self.partner_bank_id = self._get_partner_bank_id(self.company_id.id)

    def _get_partner_bank_id(self, company_id):
        company = self.env["res.company"].browse(company_id)
        if company.partner_id:
            bank = self.env["res.partner.bank"].search(
                [
                    ("partner_id", "=", company.partner_id.id),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if not bank:
                bank = self.env["res.partner.bank"].search(
                    [
                        ("partner_id", "=", company.partner_id.id),
                        ("company_id", "=", False),
                    ],
                    limit=1,
                )
            return bank
