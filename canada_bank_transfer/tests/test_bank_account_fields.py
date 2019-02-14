# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import (
    EFTCase,
)


class TestFormatEFTHeader(EFTCase):

    def test_canada_bank_account_display_name(self):
        account = self.env['res.partner.bank'].create({
            'bank_id': self.td.id,
            'canada_transit': '10001',
            'acc_number': '2000002',
            'partner_id': self.supplier_1.id,
        })
        assert account.display_name == '10001 004 2000002'

    def test_foreign_account_display_name(self):
        bank = self.env['res.bank'].create({
            'name': 'Bank of Paris',
        })
        account = self.env['res.partner.bank'].create({
            'bank_id': bank.id,
            'acc_number': 'FRXX XXXX XXXX XXXX XXXX XXXX XXX',
            'partner_id': self.supplier_1.id,
        })
        assert account.acc_number in account.display_name
