# -*- coding: utf-8 -*-
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
        "inbound_payment_method_line_ids", "outbound_payment_method_line_ids", "type"
    )
    def _check_payment_accounts_requirements(self):
        # Outstanding incoming/outgoing payment accounts must be configured
        # and exclusive to a single bank journal. The constraint fires on both
        # creation and update of the journal.
        bank_journals = self.filtered(lambda j: j.type == "bank")
        for journal in bank_journals:
            self._validate_payment_accounts_presence(journal)
            self._validate_payment_accounts_uniqueness(journal)

    def _validate_payment_accounts_presence(self, journal):
        inbound_accounts = journal.inbound_payment_method_line_ids.mapped(
            "payment_account_id"
        )
        outbound_accounts = journal.outbound_payment_method_line_ids.mapped(
            "payment_account_id"
        )

        if not inbound_accounts:
            raise ValidationError(
                _("At least one inbound payment suspense account must be configured.")
            )
        if not outbound_accounts:
            raise ValidationError(
                _("At least one outbound payment suspense account must be configured.")
            )

    def _validate_payment_accounts_uniqueness(self, journal):
        inbound_lines = journal.inbound_payment_method_line_ids
        outbound_lines = journal.outbound_payment_method_line_ids
        all_accounts = (inbound_lines + outbound_lines).mapped("payment_account_id")

        if not all_accounts:
            return

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

        # Fixed: Removed "self" argument to avoid TypeError
        if self._has_transactions():
            raise ValidationError(
                _(
                    "You cannot modify the suspense account because transactions "
                    "already exist for this journal."
                )
            )

    # Fixed: Removed the redundant 'journal' parameter
    def _has_transactions(self):
        domain = [("journal_id", "=", self.id)]
        has_move = self.env["account.move"].search_count(domain, limit=1)
        has_payment = self.env["account.payment"].search_count(domain, limit=1)
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
