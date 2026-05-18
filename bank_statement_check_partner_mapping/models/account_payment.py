# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_mapping_ids = fields.One2many(
        comodel_name="bank.statement.partner.mapping",
        inverse_name="payment_id",
        string="Generated Check Mappings",
        help="Technical field to link the payment to its generated mapping rules.",
    )

    def action_post(self):
        """
        Extend payment posting to generate a partner mapping rule for checks.
        """
        res = super().action_post()
        self._create_check_partner_mappings()
        return res

    def write(self, vals):
        """
        Extend write to catch check number assignments that happen after posting
        (e.g., when the check is actually printed).
        """
        res = super().write(vals)
        if "check_number" in vals:
            self._create_check_partner_mappings()
        return res

    def action_draft(self):
        """
        Extend resetting to draft to archive the corresponding check mapping rules.
        """
        res = super().action_draft()
        self._archive_check_partner_mappings()
        return res

    def action_cancel(self):
        """
        Extend cancellation to archive the corresponding check mapping rules.
        """
        res = super().action_cancel()
        self._archive_check_partner_mappings()
        return res

    def _create_check_partner_mappings(self):
        """
        Identify eligible check payments and create or update their partner mapping entries.
        """
        eligible_payments = self.filtered(lambda p: p._is_eligible_for_check_mapping())
        mapping_env = self.env["bank.statement.partner.mapping"]

        for payment in eligible_payments:
            vals = payment._prepare_check_mapping_vals()

            if not payment.check_mapping_ids:
                mapping_env.create(vals)
            else:
                # If the rule exists but the check number changed, we update the label
                payment.check_mapping_ids.write({
                    "label": vals["label"],
                    "active": True
                })

    def _archive_check_partner_mappings(self):
        """
        Deactivate all mapping entries directly linked to these payments.
        Using the relational link avoids string-matching issues.
        """
        self.check_mapping_ids.write({"active": False})

    def _is_eligible_for_check_mapping(self):
        """
        Check if the payment is a check printing with an assigned number.
        """
        self.ensure_one()
        is_check = self.payment_method_code == "check_printing"
        has_number = bool(self.check_number)
        return is_check and has_number

    def _prepare_check_mapping_vals(self):
        """
        Prepare values dictionary for creating a bank statement partner mapping record.
        Includes the strong relational link to the payment.
        Uses native Python 3 string formatting safely to prevent UI-induced tracebacks.
        """
        self.ensure_one()
        fmt = self.journal_id.check_format or "{check_number}"

        # Safely attempt to format the string using Python 3 standard
        try:
            mapping_label = fmt.format(check_number=self.check_number)
        except (KeyError, ValueError):
            mapping_label = str(self.check_number)

        return {
            "partner_id": self.partner_id.id,
            "label": mapping_label,
            "journal_id": self.journal_id.id,
            "mapping_type": "complete",
            "payment_id": self.id,
        }
