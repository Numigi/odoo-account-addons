# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_recuperate_partners(self):
        """
        Execute the custom partner recuperation with journal filtering and reference fallback.
        """
        if self.state != "open":
            return

        eligible_lines = self.line_ids.filtered(lambda l: not l.partner_id)
        for line in eligible_lines:
            self._process_line_mapping(line)

    def _process_line_mapping(self, line):
        """
        Find a partner for a single line using payment_ref, then fallback to ref.
        """
        mapping = self._find_mapping_for_value(line.payment_ref)
        if not mapping:
            mapping = self._find_mapping_for_value(line.ref)

        if mapping:
            line.partner_id = mapping[0].partner_id.id

    def _find_mapping_for_value(self, value):
        """
        Search complete mappings, then partial mappings for a given string value.
        """
        if not value:
            return self.env["bank.statement.partner.mapping"]

        mapping = self._search_mapping_complete(value)
        if mapping:
            return mapping

        return self._search_mapping_partial(value)

    def _search_mapping_complete(self, value):
        """
        Search complete label mappings matching the value and journal.
        """
        domain = [
            ("mapping_type", "=", "complete"),
            ("label", "=", value),
            ("journal_id", "in", [self.journal_id.id, False]),
        ]
        return self.env["bank.statement.partner.mapping"].search(domain, limit=1)

    def _search_mapping_partial(self, value):
        """
        Search partial label mappings matching the value and journal.
        """
        domain = [
            ("mapping_type", "=", "partial"),
            ("journal_id", "in", [self.journal_id.id, False]),
        ]
        all_partial_mappings = self.env["bank.statement.partner.mapping"].search(domain)
        return all_partial_mappings.filtered(lambda m: value.find(m.label) != -1)
