# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.constrains(
        "inbound_payment_method_line_ids",
        "outbound_payment_method_line_ids",
        "suspense_account_id",
        "default_account_id",
        "type",
    )
    def _check_internal_account_exclusivity(self):
        if self._should_bypass_strict_checks():
            return
        bank_journals = self.filtered(lambda j: j.type == "bank")
        for journal in bank_journals:
            journal._verify_internal_account_exclusivity()

    def _verify_internal_account_exclusivity(self):
        in_accounts = self._get_inbound_payment_accounts()
        out_accounts = self._get_outbound_payment_accounts()
        self._check_inbound_outbound_overlap(in_accounts, out_accounts)

        payment_accounts = in_accounts | out_accounts
        self._check_suspense_overlap(payment_accounts)
        self._check_default_overlap(payment_accounts)
        self._check_suspense_and_default_overlap()

    @api.constrains("default_account_id")
    def _check_default_account_id_uniqueness(self):
        if self._should_bypass_strict_checks():
            return
        bank_journals = self.filtered(
            lambda j: j.type == "bank" and j.default_account_id
        )
        for journal in bank_journals:
            journal._verify_default_account_uniqueness()

    def _verify_default_account_uniqueness(self):
        duplicate = self._get_default_account_duplicate()
        if duplicate:
            raise ValidationError(
                _("The bank account %s is already associated with journal %s.")
                % (self.default_account_id.code, duplicate.name)
            )

    @api.constrains(
        "inbound_payment_method_line_ids",
        "outbound_payment_method_line_ids",
        "type",
    )
    def _check_payment_lines_presence(self):
        if self._should_bypass_strict_checks():
            return
        bank_journals = self.filtered(lambda j: j.type == "bank")
        for journal in bank_journals:
            journal._validate_minimum_payment_lines()

    def _validate_minimum_payment_lines(self):
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
        if self._should_bypass_strict_checks():
            return
        bank_journals = self.filtered(
            lambda j: j.type == "bank" and j.suspense_account_id
        )
        for journal in bank_journals:
            journal._verify_suspense_account_uniqueness()

    def _verify_suspense_account_uniqueness(self):
        duplicate = self._get_suspense_account_duplicate()
        if duplicate:
            raise ValidationError(
                _(
                    "The suspense account %s cannot be shared between "
                    "%s and %s due to exclusivity rules."
                )
                % (self.suspense_account_id.code, self.name, duplicate.name)
            )

    def write(self, vals):
        if self._should_check_transactions(vals):
            self._check_suspense_account_transaction(vals.get("suspense_account_id"))
        return super().write(vals)

    def _should_check_transactions(self, vals):
        return "suspense_account_id" in vals and not self._should_bypass_strict_checks()

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
                    "You cannot modify the suspense account because "
                    "transactions already exist for this journal."
                )
            )

    def _should_bypass_strict_checks(self):
        return config.get("test_enable") and not self.env.context.get(
            "strict_bank_exclusivity"
        )

    def _get_inbound_payment_accounts(self):
        return set(self.inbound_payment_method_line_ids.mapped("payment_account_id"))

    def _get_outbound_payment_accounts(self):
        return set(self.outbound_payment_method_line_ids.mapped("payment_account_id"))

    def _check_inbound_outbound_overlap(self, in_accounts, out_accounts):
        if in_accounts & out_accounts:
            raise ValidationError(
                _("Inbound and outbound payment accounts must be strictly different.")
            )

    def _check_suspense_overlap(self, payment_accounts):
        if self._is_account_in_group(self.suspense_account_id, payment_accounts):
            raise ValidationError(
                _("The suspense account must be different from the payment accounts.")
            )

    def _check_default_overlap(self, payment_accounts):
        if self._is_account_in_group(self.default_account_id, payment_accounts):
            raise ValidationError(
                _(
                    "The default bank account must be different from the payment accounts."
                )
            )

    def _check_suspense_and_default_overlap(self):
        if not self.suspense_account_id or not self.default_account_id:
            return
        if self.suspense_account_id == self.default_account_id:
            raise ValidationError(
                _("The default bank account and suspense account must be different.")
            )

    def _is_account_in_group(self, account, account_group):
        if not account:
            return False
        return account in account_group

    def _get_default_account_duplicate(self):
        domain = [
            ("type", "=", "bank"),
            ("default_account_id", "=", self.default_account_id.id),
            ("id", "!=", self.id),
        ]
        return self.search(domain, limit=1)

    def _get_suspense_account_duplicate(self):
        domain = [
            ("type", "=", "bank"),
            ("suspense_account_id", "=", self.suspense_account_id.id),
            ("id", "!=", self.id),
        ]
        if self._is_edit_mode():
            domain.append(("reconcile_mode", "=", "keep"))
        return self.search(domain, limit=1)

    def _is_edit_mode(self):
        return self.reconcile_mode == "edit"

    def _has_transactions(self):
        domain = [("journal_id", "=", self.id)]
        has_move = self._has_record("account.move", domain)
        has_payment = self._has_record("account.payment", domain)
        has_stmt = self._has_record("account.bank.statement", domain)
        has_line = self._has_record("account.bank.statement.line", domain)
        return bool(has_move or has_payment or has_stmt or has_line)

    def _has_record(self, model_name, domain):
        return bool(self.env[model_name].search_count(domain, limit=1))
