# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAuditlogRule(TransactionCase):
    def test_journal_auditlog_rule_is_subscribed(self):
        rule = self.env.ref(
            "account_journal_bank_exclusivity.auditlog_rule_account_journal"
        )
        self.assertEqual(rule.state, "subscribed")
