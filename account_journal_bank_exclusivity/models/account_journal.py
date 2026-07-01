# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.constrains("default_account_id")
    def _check_default_account_id_uniqueness(self):
        bank_journals = self.filtered(
            lambda j: j.type == "bank" and j.default_account_id
        )
        for journal in bank_journals:
            self._verify_account_uniqueness(journal)

    def _verify_account_uniqueness(self, journal):
        duplicate = self.search(
            [
                ("type", "=", "bank"),
                ("default_account_id", "=", journal.default_account_id.id),
                ("id", "!=", journal.id),
            ],
            limit=1,
        )
        if duplicate:
            raise ValidationError(
                _("The bank account %s is already associated with journal %s.")
                % (journal.default_account_id.code, duplicate.name)
            )

    @api.constrains(
        "inbound_payment_method_line_ids",
        "outbound_payment_method_line_ids",
        "type",
    )
    def _check_payment_lines_presence(self):
        from odoo.tools import config

        # Bypass during automated tests to avoid breaking Odoo's standard chart template loading
        if config.get("test_enable") and not self.env.context.get(
            "strict_bank_exclusivity"
        ):
            return

        bank_journals = self.filtered(lambda j: j.type == "bank")
        for journal in bank_journals:
            journal._validate_minimum_payment_lines()

    def _validate_minimum_payment_lines(self):
        # Prevent saving a journal if payment method lines are completely removed
        if not self.inbound_payment_method_line_ids:
            raise ValidationError(
                _("At least one inbound payment method must be configured.")
            )
        if not self.outbound_payment_method_line_ids:
            raise ValidationError(
                _("At least one outbound payment method must be configured.")
            )

    @api.constrains("suspense_account_id", "reconcile_mode")
    def _check_suspense_account_exclusivity(self):
        # Apply checks to all bank journals that have a suspense account configured
        bank_journals = self.filtered(
            lambda j: j.type == "bank" and j.suspense_account_id
        )
        for journal in bank_journals:
            journal._verify_suspense_account_uniqueness()

    def _verify_suspense_account_uniqueness(self):
        domain = [
            ("type", "=", "bank"),
            ("suspense_account_id", "=", self.suspense_account_id.id),
            ("id", "!=", self.id),
        ]

        # If the current journal is in 'modify' mode, we only check
        # conflicts with 'keep' journals.
        # If it is in 'keep' mode, it must be globally unique across ALL bank journals.
        if self.reconcile_mode != "keep":
            domain.append(("reconcile_mode", "=", "keep"))

        duplicate = self.search(domain, limit=1)
        if duplicate:
            raise ValidationError(
                _(
                    "The suspense account %s cannot be shared between "
                    "%s and %s due to exclusivity rules."
                )
                % (self.suspense_account_id.code, self.name, duplicate.name)
            )

    def write(self, vals):
        if "suspense_account_id" in vals:
            self._check_suspense_account_transaction(vals.get("suspense_account_id"))
        return super().write(vals)

    def _check_suspense_account_transaction(self, new_account_id):
        target_journals = self.filtered(
            lambda j: j.type == "bank" and j.reconcile_mode == "keep"
        )
        for journal in target_journals:
            journal._verify_suspense_account_change(new_account_id)

    def _verify_suspense_account_change(self, new_account_id):
        if self.suspense_account_id.id == new_account_id:
            return
        if self._has_transactions():
            raise ValidationError(
                _(
                    "You cannot modify the suspense account because transactions "
                    "already exist for this journal."
                )
            )

    def _has_transactions(self):
        domain = [("journal_id", "=", self.id)]
        has_move = self.env["account.move"].search_count(domain, limit=1)
        has_payment = self.env["account.payment"].search_count(domain, limit=1)
        has_stmt = self.env["account.bank.statement"].search_count(domain, limit=1)
        has_line = self.env["account.bank.statement.line"].search_count(domain, limit=1)
        return bool(has_move or has_payment or has_stmt or has_line)
