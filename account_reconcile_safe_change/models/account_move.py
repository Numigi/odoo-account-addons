# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _

from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("state")
    def _check_state(self):
        for rec in self:
            if rec.statement_line_id or any(
                line.statement_line_id for line in rec.line_ids
            ):
                # TODO : verrou complet ou juste un passage d'un statut comptabilisé à un autre (draft, cancel) ?
                raise ValidationError(
                    _(
                        "You cannot modify this Account Move because"
                        " it is linked to a Bank Statement Line."
                        " Please modify the Statement Line."
                    )
                )
            if rec.payment_id and rec.payment_id.statement_line_ids:
                raise ValidationError(
                    _(
                        "This Account Move is linked to a Payment"
                        " on which the Bank Reconciliation has been"
                        " done. You must first cancel the Bank"
                        " Reconciliation of the Payment."
                    )
                )
