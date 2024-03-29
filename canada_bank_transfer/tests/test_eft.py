# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
import pytest
from .common import EFTCase
from odoo.exceptions import ValidationError, UserError


class AccountEFTCase(EFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pmt_1 = cls.generate_payment(cls.td_account, 111.11)
        cls.pmt_2 = cls.generate_payment(cls.rbc_account, 222.22)
        cls.expected_total = 333.33
        cls.payments = cls.pmt_1 | cls.pmt_2


class TestCreateEFTFromPayments(AccountEFTCase):

    def _create_eft_from_payments(self):
        action = self.env['account.eft'].create_eft_from_payments(
            self.payments)
        return self.env['account.eft'].browse(action['res_id'])

    def test_payments_are_asigned_to_eft(self):
        eft = self._create_eft_from_payments()
        assert eft.payment_ids == self.payments

    def test_payments_are_asigned_to_eft_then_cancel_payment(self):
        self._create_eft_from_payments()
        with pytest.raises(UserError):
            self.pmt_1.action_draft()
        with pytest.raises(UserError):
            self.pmt_2.action_draft()

    def test_state_is_draft(self):
        eft = self._create_eft_from_payments()
        assert eft.state == 'draft'

    def test_eft_name_is_computed_on_create(self):
        eft = self._create_eft_from_payments()
        assert eft.name == "EFT{0:0>4}".format(eft.id)

    def test_raise_error_if_payments_have_different_journals(self):
        new_journal = self.journal.copy()
        self.payments |= self.pmt_1.copy({'journal_id': new_journal.id})
        with pytest.raises(ValidationError):
            self._create_eft_from_payments()

    def test_raise_error_if_payment_method_is_not_eft(self):
        self.pmt_2.payment_method_id = self.env.ref(
            'account.account_payment_method_manual_in')
        with pytest.raises(ValidationError):
            self._create_eft_from_payments()

    def test_raise_error_if_payment_is_not_posted(self):
        self.payments |= self.pmt_1.copy({'state': 'draft'})
        with pytest.raises(ValidationError):
            self._create_eft_from_payments()

    def test_raise_error_if_payment_is_sent(self):
        self.pmt_1.is_move_sent = True
        with pytest.raises(ValidationError):
            self._create_eft_from_payments()

    def test_bank_account_is_automatically_assigned(self):
        self.pmt_1.partner_bank_id = False
        self.pmt_2.partner_bank_id = False

        self._create_eft_from_payments()

        assert self.pmt_1.partner_bank_id == self.td_account
        assert self.pmt_2.partner_bank_id == self.rbc_account

    def test_eft_total_is_total_of_payments(self):
        eft = self._create_eft_from_payments()
        assert eft.total == self.expected_total

    def test_eft_journal_is_journal_of_payments(self):
        eft = self._create_eft_from_payments()
        assert eft.journal_id == self.journal

    def test_eft_currency_is_journal_currency(self):
        eft = self._create_eft_from_payments()
        assert eft.currency_id == self.env.ref('base.CAD')


class TestGenerateEFTFile(AccountEFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eft = cls.env['account.eft'].create({
            'payment_ids': [(6, 0, cls.payments.ids)],
            'journal_id': cls.journal.id,
        })
        cls.eft.action_approve()

    def test_content_binary_is_filled(self):
        assert not self.eft.content_binary
        self.eft.generate_eft_file()
        assert self.eft.content_binary

    def test_content_is_filled(self):
        assert not self.eft.content
        self.eft.generate_eft_file()
        assert self.eft.content

    def test_filename_is_filled(self):
        assert not self.eft.filename
        self.eft.generate_eft_file()
        assert self.eft.filename == "{}-{}.txt".format(
            self.eft.name, self.eft.sequence)

    def test_raise_error_if_bank_account_is_not_selected(self):
        self.pmt_1.partner_bank_id = False
        with pytest.raises(ValidationError):
            self.eft.generate_eft_file()

    def test_raise_error_if_bank_is_not_selected(self):
        self.pmt_1.partner_bank_id.bank_id = False
        with pytest.raises(ValidationError):
            self.eft.generate_eft_file()

    def test_raise_error_if_institution_is_not_filled(self):
        self.pmt_1.partner_bank_id.bank_id.canada_institution = False
        with pytest.raises(ValidationError):
            self.eft.generate_eft_file()

    def test_raise_error_if_transit_is_not_filled(self):
        self.pmt_1.partner_bank_id.canada_transit = False
        with pytest.raises(ValidationError):
            self.eft.generate_eft_file()

    def test_raise_error_if_account_number_is_not_digit(self):
        self.pmt_1.partner_bank_id.acc_number = '123456a'
        with pytest.raises(ValidationError):
            self.eft.generate_eft_file()

    def test_file_number_of_eft_is_the_sequence_number(self):
        self.eft.generate_eft_file()
        assert self.eft.content[20:24] == "{0:0>4}".format(self.eft.sequence)


class TestEFTConfirmationWizard(AccountEFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eft = cls.env['account.eft'].create({
            'payment_ids': [(6, 0, cls.payments.ids)],
            'journal_id': cls.journal.id,
        })
        cls.eft.validate_payments()
        cls.eft.action_approve()
        cls.eft.generate_eft_file()
        cls.eft_date = datetime.now().date() + timedelta(30)
        cls.eft.payment_date = cls.eft_date

    def _open_confirmation_wizard(self):
        action = self.eft.action_done()
        return self.env['account.eft.confirmation.wizard'].browse(action['res_id'])

    def test_on_eft_confirmation__wizard_lines_are_completed_by_default(self):
        wizard = self._open_confirmation_wizard()
        assert wizard.mapped('line_ids.completed') == [True, True]

    def test_on_eft_confirmation__eft_state_set_to_done(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.eft.state == 'done'

    def test_on_eft_confirmation__payments_are_sent(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.pmt_1.is_move_sent
        assert self.pmt_2.is_move_sent

    def test_on_eft_confirmation__failed_payments_are_not_sent(self):
        wizard = self._open_confirmation_wizard()
        wizard.line_ids.filtered(
            lambda l: l.payment_id == self.pmt_1).completed = False
        wizard.action_validate()
        assert not self.pmt_1.is_move_sent
        assert self.pmt_2.is_move_sent

    def test_on_eft_confirmation__payment_date_is_set_to_eft_date(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.pmt_1.date == self.eft_date

    def test_on_eft_confirmation__payment_move_is_posted(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.pmt_1.move_id.state == 'posted'

    def test_on_eft_confirmation__payment_move_date_is_set_to_eft_date(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.pmt_1.move_id.date == self.eft_date

    def test_on_eft_confirmation__payment_move_line_date_maturity_is_set_to_eft_date(self):
        wizard = self._open_confirmation_wizard()
        wizard.action_validate()
        assert self.pmt_1.mapped('line_ids.date_maturity') == [
            self.eft_date, self.eft_date]

    def test_on_eft_confirmation__failed_payment_date_is_not_set_to_eft_date(self):
        wizard = self._open_confirmation_wizard()
        wizard.line_ids.filtered(
            lambda l: l.payment_id == self.pmt_1).completed = False
        wizard.action_validate()
        assert self.pmt_1.date != self.eft_date
        assert self.pmt_2.date == self.eft_date


class TestEFTWorkflow(AccountEFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eft = cls.env['account.eft'].create({
            'payment_ids': [(6, 0, cls.payments.ids)],
            'journal_id': cls.journal.id,
        })

    def test_approve(self):
        assert self.eft.state == 'draft'
        self.eft.action_approve()
        assert self.eft.state == 'approved'

    def test_set_to_draft(self):
        self.eft.action_approve()
        assert self.eft.state == 'approved'
        self.eft.action_draft()
        assert self.eft.state == 'draft'

    def test_unlink_not_possible_if_not_draft(self):
        self.eft.action_approve()
        with pytest.raises(ValidationError):
            self.eft.unlink()
