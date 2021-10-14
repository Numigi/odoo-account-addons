# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests.common import SavepointCase


class TestAccountCheckDeposit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payable = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "210110",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner",
                "property_account_payable_id": cls.payable.id,
            }
        )

        cls.check_journal = cls.env["account.journal"].create(
            {
                "name": "Check Journal",
                "type": "bank",
                "code": "CH",
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {
                "name": "Bank Journal",
                "type": "bank",
                "code": "BNK",
            }
        )
        cls.payment = cls.env["account.payment"].create(
            {
                "journal_id": cls.check_journal.id,
                "partner_id": cls.partner.id,
                "amount": 100,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "partner_type": "customer",
                "payment_type": "inbound",
            }
        )
        cls.payment.post()
        cls.payment_move_line = cls.payment.move_line_ids.filtered(
            lambda l: l.account_id == cls.check_journal.default_debit_account_id
        )

        cls.deposit = cls.env["account.check.deposit"].create(
            {
                "deposit_date": datetime.now().date(),
                "currency_id": cls.env.user.company_id.currency_id.id,
                "journal_id": cls.check_journal.id,
                "bank_journal_id": cls.bank_journal.id,
                "check_payment_ids": [(4, cls.payment_move_line.id)],
            }
        )

    def test_debit_move_line_has_company(self):
        self.deposit.validate_deposit()
        debit = self.deposit.line_ids.filtered(lambda l: l.debit)
        assert debit.partner_id == self.env.user.company_id.partner_id
        credit = self.deposit.line_ids.filtered(lambda l: l.credit)
        assert credit.partner_id == self.partner
