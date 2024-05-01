# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_recuperate_partners(self):
        """Recuperate Partners ."""
        if self.state == "open":
            for line in self.line_ids.filtered(
                lambda line_statement: not line_statement.partner_id
            ):
                mapping_types = self.env["bank.statement.partner.mapping"].search(
                    [("label", "=", line.payment_ref)]
                )
                if not mapping_types:
                    mapping_types = (
                        self.env["bank.statement.partner.mapping"]
                        .search([("mapping_type", "=", "partial")])
                        .filtered(
                            lambda mapping_type: line.payment_ref.find(
                                mapping_type.label
                            )
                            != -1
                        )
                    )
                line.partner_id = (
                    mapping_types and mapping_types[0].partner_id.id or False
                )
