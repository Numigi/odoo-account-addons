# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _

from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.constrains("state")
    def _check_state(self):
        for rec in self:
            if (
                rec.statement_line_ids
            ):  # TODO : est-ce que ce champ est uniquement renseigné si c'est comptabilisé ou comment ?
                # TODO : même cas que account move, un verrou complet ou un passage d'un statut comptabilisé à un autre (draft, cancel) ?
                raise ValidationError(
                    _(
                        "You cannot modify this Payment because a Bank"
                        " Statement Line is linked."
                        " You need to cancel the Bank Reconciliation first."
                    )
                )
