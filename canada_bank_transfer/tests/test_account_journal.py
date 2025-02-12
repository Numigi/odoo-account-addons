# Copyright 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command
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
        journal.write(
            {
                "outbound_payment_method_line_ids": [
                    Command.create({"payment_method_id": self.eft_method.id})
                ]
            }
        )
        assert journal.eft_sequence_id
