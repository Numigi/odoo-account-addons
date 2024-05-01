# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestJournalChronology(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_on_create_journal(self):
        # Create sale account journal
        my_journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "sale",
                "code": "TEST",
            }
        )
        self.assertTrue(my_journal.check_chronology)

    def test_on_write_journal_type(self):
        # Create sale account journal
        general_journal = self.env["account.journal"].create(
            {
                "name": "General Journal",
                "type": "general",
                "code": "GJ",
            }
        )
        self.assertFalse(general_journal.check_chronology)

        general_journal.write({"type": "sale"})
        self.assertTrue(general_journal.check_chronology)
