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
        "inbound_payment_method_line_ids", "outbound_payment_method_line_ids"
    )
    def _check_suspense_accounts_requirements(self):
        bank_journals = self.filtered(lambda j: j.type == "bank")
        for journal in bank_journals:
            self._validate_suspense_accounts_presence(journal)
            self._validate_suspense_accounts_uniqueness(journal)

    def _validate_suspense_accounts_presence(self, journal):
        inbound_lines = journal.inbound_payment_method_line_ids
        outbound_lines = journal.outbound_payment_method_line_ids
        in_accounts = inbound_lines.mapped("payment_account_id")
        out_accounts = outbound_lines.mapped("payment_account_id")
        if not in_accounts:
            raise ValidationError(
                _("At least one inbound payment suspense account must be configured.")
            )
        if not out_accounts:
            raise ValidationError(
                _("At least one outbound payment suspense account must be configured.")
            )

    def _validate_suspense_accounts_uniqueness(self, journal):
        inbound_lines = journal.inbound_payment_method_line_ids
        outbound_lines = journal.outbound_payment_method_line_ids
        all_accounts = (inbound_lines + outbound_lines).mapped("payment_account_id")
        duplicate_line = self.env["account.payment.method.line"].search(
            [
                ("payment_account_id", "in", all_accounts.ids),
                ("journal_id", "!=", journal.id),
                ("journal_id.type", "=", "bank"),
            ],
            limit=1,
        )
        if duplicate_line:
            raise ValidationError(
                _("The payment account %s is already used in journal %s.")
                % (
                    duplicate_line.payment_account_id.code,
                    duplicate_line.journal_id.name,
                )
            )

    @api.constrains("suspense_account_id", "reconcile_mode")
    def _check_suspense_account_exclusivity(self):
        target_journals = self.filtered(
            lambda j: j.type == "bank"
            and j.reconcile_mode == "keep"
            and j.suspense_account_id
        )
        for journal in target_journals:
            self._verify_suspense_account_uniqueness(journal)

    def _verify_suspense_account_uniqueness(self, journal):
        duplicate = self.search(
            [
                ("type", "=", "bank"),
                ("reconcile_mode", "=", "keep"),
                ("suspense_account_id", "=", journal.suspense_account_id.id),
                ("id", "!=", journal.id),
            ],
            limit=1,
        )
        if duplicate:
            raise ValidationError(
                _(
                    "The suspense account %s is exclusive and already used by journal %s."
                )
                % (journal.suspense_account_id.code, duplicate.name)
            )

    @api.constrains("suspense_account_id")
    def _check_suspense_account_modification(self):
        target_journals = self.filtered(
            lambda j: j.type == "bank" and j.reconcile_mode == "keep"
        )
        for journal in target_journals:
            self._verify_suspense_account_unchanged(journal)

    def _verify_suspense_account_unchanged(self, journal):
        if not self._has_transactions(journal):
            return
        if journal.suspense_account_id != journal._origin.suspense_account_id:
            raise ValidationError(
                _(
                    "You cannot modify the suspense account because transactions "
                    "already exist for this journal."
                )
            )

    def _has_transactions(self, journal):
        domain = [("journal_id", "=", journal.id)]
        has_move = self.env["account.move"].search_count(domain, limit=1)
        has_payment = self.env["account.payment"].search_count(domain, limit=1)
        has_stmt = False
        if "account.bank.statement" in self.env:
            has_stmt = self.env["account.bank.statement"].search_count(domain, limit=1)
        has_line = self.env["account.bank.statement.line"].search_count(domain, limit=1)
        return bool(has_move or has_payment or has_stmt or has_line)

    @api.constrains("reconcile_mode")
    def _check_reconcile_mode_change(self):
        target_journals = self.filtered(
            lambda j: j.type == "bank" and j.reconcile_mode == "keep"
        )
        for journal in target_journals:
            if journal.reconcile_mode != journal._origin.reconcile_mode:
                self._verify_suspense_account_uniqueness(journal)
