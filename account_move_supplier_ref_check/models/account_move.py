# Copyright 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("ref", "move_type", "partner_id", "journal_id", "state")
    def _check_duplicate_supplier(self):
        """This function enhances the duplicate vendor bill constraint
        by modifying the reference check to validate duplicates
        based solely on `partner_id` and `ref`.

        This have wider condition scope comparing to the original function :
        _check_duplicate_supplier_reference().

        """

        moves = self.filtered(
            lambda move: move.state == "posted"
            and move.is_purchase_document()
            and move.ref
        )

        if not moves:
            return

        self.env["account.move"].flush(
            [
                "ref",
                "move_type",
                "invoice_date",
                "journal_id",
                "company_id",
                "partner_id",
                "commercial_partner_id",
            ]
        )
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        self._cr.execute(
            """
            SELECT move2.id
            FROM account_move move
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_partner partner ON partner.id = move.partner_id
            INNER JOIN account_move move2 ON
                move2.ref = move.ref
                AND move2.company_id = journal.company_id
                AND move2.commercial_partner_id = partner.commercial_partner_id
                AND move2.move_type = move.move_type
                AND move2.id != move.id
            WHERE move.id IN %s
        """,
            [tuple(moves.ids)],
        )
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(
                _(
                    "Duplicated vendor reference detected. You probably encoded "
                    "twice the same vendor bill/credit note:\n%s"
                )
                % "\n".join(
                    duplicated_moves.mapped(
                        lambda m: "%(partner)s - %(ref)s "
                        % {
                            "ref": m.ref,
                            "partner": m.partner_id.display_name,
                        }
                    )
                )
            )
