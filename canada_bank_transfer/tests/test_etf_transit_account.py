# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import EFTCase


class EtfTransitAccountCase(EFTCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "canada_bank_transfer.use_transit_account", True
        )
        cls.account_transit = cls.env["account.account"].create(
            {
                "code": "BK",
                "name": "Transit account",
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            }
        )
        cls.journal.transit_account = cls.account_transit.id
        cls.payable = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "210110",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )
        cls.partner = cls.env.ref("base.res_partner_3")
        cls.partner.property_account_payable_id = cls.payable.id
        cls.bc = cls.env["res.bank"].create(
            {
                "name": "Bank of Canada",
                "canada_institution": "005",
            }
        )
        cls.partner_account_bank = cls.env["res.partner.bank"].create(
            {
                "bank_id": cls.bc.id,
                "canada_transit": "30005",
                "acc_number": "3000005",
                "partner_id": cls.partner.id,
            }
        )

        cls.payment_1 = cls.generate_payment(cls.partner_account_bank, 500)
        cls.payment_2 = cls.generate_payment(cls.partner_account_bank, 700)
        cls.payments = cls.payment_1 | cls.payment_2

    def test_transit_account_payment(self):
        assert self.account_transit in self.payment_1.move_line_ids.mapped("account_id")


class TestTransitMoveCase(EtfTransitAccountCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eft = cls.env["account.eft"].create(
            {
                "payment_ids": [(6, 0, cls.payments.ids)],
                "journal_id": cls.journal.id,
            }
        )
        cls.journal.update_posted = True
        cls.eft.validate_payments()
        cls.eft.action_approve()
        cls.eft.generate_eft_file()

    def test_deposit_move(self):
        wizard = self._open_confirmation_wizard_etf()
        wizard.line_ids.filtered(
            lambda l: l.payment_id == self.payment_1
        ).completed = False
        wizard.action_validate()
        move = self.eft.deposit_account_move_id
        assert move
        debit_line = move.line_ids.filtered("debit")
        credit_line = move.line_ids.filtered("credit")
        assert debit_line.account_id == self.account_transit
        assert debit_line.amount_currency == 700
        assert credit_line.account_id == self.eft.journal_id.default_debit_account_id
        assert credit_line.amount_currency == -700

    def test_move_deleted_on_cancel(self):
        wizard = self._open_confirmation_wizard_etf()
        wizard.action_validate()
        self.eft.action_cancel()
        assert not self.eft.deposit_account_move_id

    def test_move_lines_reconciled(self):
        wizard = self._open_confirmation_wizard_etf()
        wizard.action_validate()
        move = self.eft.deposit_account_move_id
        lines = move.line_ids.filtered("debit")
        line_1 = lines.filtered(lambda l: l.amount_currency == 500)
        line_2 = lines.filtered(lambda l: l.amount_currency == 700)
        assert line_1.reconciled
        assert line_2.reconciled
        assert line_1.mapped("matched_credit_ids.credit_move_id.payment_id") == self.payment_1
        assert line_2.mapped("matched_credit_ids.credit_move_id.payment_id") == self.payment_2

    def _open_confirmation_wizard_etf(self):
        action = self.eft.action_done()
        return self.env["account.eft.confirmation.wizard"].browse(action["res_id"])
