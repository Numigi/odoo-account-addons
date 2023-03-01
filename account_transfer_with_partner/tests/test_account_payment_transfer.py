from odoo.addons.test_mail.tests.common import mail_new_test_user
from odoo.tests import common
import time


class TestAccountPaymentTransfer(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Prepare Users and Bank Statements."""
        super(TestAccountPaymentTransfer, cls).setUpClass()
        cls.currency_cad_id = cls.env.ref("base.CAD").id
        cls.bank_journal_1 = cls.env['account.journal'].create({'name': 'Bank 1', 'type': 'bank', 'code': 'BNK67'})

        cls.bank_journal_2 = cls.env['account.journal'].create(
            {'name': 'Bank 2', 'type': 'bank', 'code': 'BNK68', 'currency_id': cls.currency_cad_id})

        cls.payment_method_manual_out = cls.env.ref("account.account_payment_method_manual_out")

        cls.payment_bank2bank = cls.env['account.partner'].create({
            'payment_date': time.strftime('%Y') + '-07-15',
            'payment_type': 'transfer',
            'amount': 50,
            'currency_id': cls.currency_cad_id,
            'journal_id': cls.bank_journal_1.id,
            'destination_journal_id': cls.bank_journal_2.id,
            'payment_method_id': cls.payment_method_manual_out.id,
        })

        cls.payment_bank2bank.post()

        cls.payment_bank2cash = cls.env['account.partner'].create({
            'payment_date': time.strftime('%Y') + '-07-15',
            'payment_type': 'transfer',
            'amount': 50,
            'currency_id': cls.currency_cad_id,
            'journal_id': cls.bank_journal_1.id,
            'destination_journal_id': cls.bank_journal_2.id,
            'payment_method_id': cls.payment_method_manual_out.id,
        })

        cls.payment_bank2bank.post()


    def test_internal_transfer_journal_items_partner(self):
        company = self.payment_bank2bank.company_id

        assert self.payment.move_line_ids
        assert self.payment.move_line_ids.mapped('partner_id')[0] == company.partner_id