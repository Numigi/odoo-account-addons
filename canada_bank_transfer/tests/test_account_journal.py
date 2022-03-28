# © 2019 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import EFTCase


class TestAccountJournal(EFTCase):
    def test_eft_sequence(self):
        assert self.journal.eft_sequence_id

    def test_eft_sequence__write(self):
        journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "bank",
                "code": "TJ",
            }
        )
        assert not journal.eft_sequence_id
        journal.outbound_payment_method_ids = self.eft_method
        assert journal.eft_sequence_id
