# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
import time


class TestAccountPaymentInternalTransfer(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentInternalTransfer, cls).setUpClass()
        cls.payment_model = cls.env['account.payment']
        cls.payment_method_manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.currency_usd_id = cls.env.ref('base.USD').id
        cls.currency_cad_id = cls.env.ref("base.CAD").id
        cls.bank_journal_1 = cls.env['account.journal'].create({'name': 'Bank 1',
                                                                'type': 'bank',
                                                                'code': 'BNK67',
                                                                'currency_id': cls.currency_usd_id})

        cls.bank_journal_2 = cls.env['account.journal'].create(
            {'name': 'Bank 2', 'type': 'bank', 'code': 'BNK68', 'currency_id': cls.currency_cad_id})


        cls.payment = cls.payment_model.create({
            'payment_date': time.strftime('%Y') + '-07-15',
            'payment_type': 'transfer',
            'amount': 50,
            'currency_id': cls.currency_cad_id,
            'journal_id': cls.bank_journal_1.id,
            'destination_journal_id': cls.bank_journal_2.id,
            'payment_method_id': cls.payment_method_manual_out.id,
        })

        cls.payment.post()

      

    def test_internal_transfer_partner(self):
        company = self.payment.company_id
        assert len(self.payment.move_line_ids) > 0
        assert all(
            partner == company.partner_id
            for partner in self.payment.move_line_ids.mapped('partner_id')
        )

