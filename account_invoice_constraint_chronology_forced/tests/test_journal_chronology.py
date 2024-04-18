# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestJournalChronology(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_on_change_type__on_journal(self):
        # Create purchase account journal then change it to sale
        my_journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "purchase",
                "code": "TEST",
            }
        )
        self.assertEqual(my_journal.check_chronology, False)
        my_journal.type = "sale"
        my_journal._onchange_type()
        self.assertEqual(my_journal.check_chronology, True)

    def test_on_create_journal(self):
        # Create sale account journal
        my_journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "sale",
                "code": "TEST",
            }
        )
        self.assertEqual(my_journal.check_chronology, True)
