# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class PaymentWizardCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'My Employee',
            'login': 'employee@example.com',
            'email': 'employee@example.com',
            'groups_id': [
                (5, 0),
                (4, cls.env.ref('base.group_user').id),
            ],
        })

        cls.payment_journal = cls.env['account.journal'].create({
            'name': 'My Bank Account',
            'code': 'BNK1',
            'type': 'bank',
        })

        cls.customer_a = cls.env['res.partner'].create({
            'name': 'Customer A',
            'customer': True,
            'is_company': True,
        })

        cls.contact_a1 = cls.env['res.partner'].create({
            'name': 'Contact A1',
            'customer': True,
            'parent_id': cls.customer_a.id,
            'type': 'contact',
        })

        cls.contact_a2 = cls.env['res.partner'].create({
            'name': 'Contact A2',
            'customer': True,
            'parent_id': cls.customer_a.id,
            'type': 'contact',
        })

        cls.customer_b = cls.env['res.partner'].create({
            'name': 'Customer B',
            'customer': True,
            'is_company': True,
        })

        cls.payment_method = cls.env.ref('account.account_payment_method_manual_in')
        cls.sale_journal = cls.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        cls.receivable_account = cls.env['account.account'].create({
            'name': 'Receivable',
            'code': '111211',
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })
        cls.revenue_account = cls.env['account.account'].create({
            'name': 'Revenue',
            'code': '444144',
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id,
        })
        cls.writeoff_account = cls.env['account.account'].create({
            'name': 'Write-Off',
            'code': '511555',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
        })
        cls.payable_account = cls.env['account.account'].create({
            'name': 'Payable',
            'code': '222222',
            'user_type_id': cls.env.ref('account.data_account_type_payable').id,
            'reconcile': True,
        })

    @classmethod
    def _generate_receivable(
        cls, amount, amount_currency=None, currency=None, account=None,
        partner=None, no_partner=False
    ):
        receivable_account = account or cls.receivable_account
        partner = partner or cls.customer_a
        move = cls.env['account.move'].create({
            'journal_id': cls.sale_journal.id,
            'line_ids': [
                (0, 0, {
                    'partner_id': None if no_partner else partner.id,
                    'account_id': receivable_account.id,
                    'name': '/',
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency,
                    'currency_id': currency.id if currency else None,
                }),
                (0, 0, {
                    'account_id': cls.revenue_account.id,
                    'name': '/',
                    'debit': -amount if amount < 0 else 0,
                    'credit': amount if amount > 0 else 0,
                })
            ]
        })
        move.post()
        return move.line_ids.filtered(lambda l: l.account_id == receivable_account)

    def _open_wizard(self, move_lines):
        action = move_lines.open_payment_from_move_line_wizard()
        return self.env['account.payment.from.move.line'].browse(action['res_id'])

    def _validate_wizard(self, wizard):
        wizard.journal_id = self.payment_journal
        wizard.payment_method_id = self.payment_method
        action = wizard.validate()
        return self.env['account.payment'].browse(action['res_id'])

    def _is_reconciled(self, move_line):
        return bool(move_line.full_reconcile_id)


@ddt
class TestPaymentWizard(PaymentWizardCase):

    def test_if_payment_amount_is_sum_of_debits(self):
        move_1 = self._generate_receivable(100)
        move_2 = self._generate_receivable(200)
        wizard = self._open_wizard(move_1 | move_2)
        assert wizard.amount == 300

    def test_if_credit_in_receivable_move_lines__credit_amount_deduced(self):
        move_1 = self._generate_receivable(100)
        move_2 = self._generate_receivable(-25)
        wizard = self._open_wizard(move_1 | move_2)
        assert wizard.amount == 75

    @data('base.CAD', 'base.EUR')
    def test_if_receivable_in_foreign_currency__payment_in_foreign_currency(self, currency_ref):
        currency = self.env.ref(currency_ref)
        move_1 = self._generate_receivable(100, amount_currency=150, currency=currency)
        move_2 = self._generate_receivable(200, amount_currency=250, currency=currency)
        wizard = self._open_wizard(move_1 | move_2)
        assert wizard.amount == 400
        assert wizard.currency_id == currency

    @data('base.CAD', 'base.EUR')
    def test_if_credit_receivable_in_foreign_currency__credit_amount_deduced(self, currency_ref):
        currency = self.env.ref(currency_ref)
        move_1 = self._generate_receivable(100, amount_currency=150, currency=currency)
        move_2 = self._generate_receivable(-20, amount_currency=-25, currency=currency)
        wizard = self._open_wizard(move_1 | move_2)
        assert wizard.amount == 125
        assert wizard.currency_id == currency

    def test_payment_difference_with_debits_in_company_currency(self):
        move_1 = self._generate_receivable(100)
        move_2 = self._generate_receivable(200)
        wizard = self._open_wizard(move_1 | move_2)
        wizard.amount = 175
        assert wizard.payment_difference == 125

    @data('base.CAD', 'base.EUR')
    def test_payment_difference_in_foreign_currency(self, currency_ref):
        currency = self.env.ref(currency_ref)
        move_1 = self._generate_receivable(100, amount_currency=150, currency=currency)
        move_2 = self._generate_receivable(200, amount_currency=250, currency=currency)
        wizard = self._open_wizard(move_1 | move_2)
        wizard.amount = 175
        assert wizard.payment_difference == 225

    def test_after_validate__payment_is_reconciled(self):
        receivable = self._generate_receivable(100)
        wizard = self._open_wizard(receivable)
        self._validate_wizard(wizard)
        assert self._is_reconciled(receivable)

    def test_after_validate__if_open_difference__payment_is_not_reconciled(self):
        receivable = self._generate_receivable(100)
        wizard = self._open_wizard(receivable)
        wizard.amount = 75
        wizard.payment_difference_handling = 'open'
        self._validate_wizard(wizard)
        assert not self._is_reconciled(receivable)

    def test_after_validate__if_reconcile_difference__payment_is_not_reconciled(self):
        receivable = self._generate_receivable(100)
        wizard = self._open_wizard(receivable)
        wizard.amount = 75
        wizard.payment_difference_handling = 'reconcile'
        wizard.writeoff_account_id = self.writeoff_account
        self._validate_wizard(wizard)
        assert self._is_reconciled(receivable)


class TestSelectableMoveLineConstraints(PaymentWizardCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receivable_1 = cls._generate_receivable(100)
        cls.receivable_2 = cls._generate_receivable(200)

    def test_if_no_line_selected__raise_error(self):
        with pytest.raises(UserError):
            self._open_wizard(self.env['account.move.line'])

    def test_if_not_posted__raise_error(self):
        self.sale_journal.update_posted = True
        self.receivable_1.move_id.button_cancel()

        with pytest.raises(UserError):
            self._open_wizard(self.receivable_1)

    def test_if_not_receivable_account__raise_error(self):
        payable = self._generate_receivable(100, account=self.payable_account)

        with pytest.raises(UserError):
            self._open_wizard(payable)

    def test_if_no_partner__raise_error(self):
        receivable_1 = self._generate_receivable(100, no_partner=True)

        with pytest.raises(UserError):
            self._open_wizard(receivable_1)

    def test_if_reconciled__raise_error(self):
        wizard = self._open_wizard(self.receivable_1)
        self._validate_wizard(wizard)
        assert self._is_reconciled(self.receivable_1)

        with pytest.raises(UserError):
            self._open_wizard(self.receivable_1 | self.receivable_2)

    def test_if_different_partners__raise_error(self):
        receivable_1 = self._generate_receivable(100, partner=self.customer_a)
        receivable_2 = self._generate_receivable(200, partner=self.customer_b)

        with pytest.raises(UserError):
            self._open_wizard(receivable_1 | receivable_2)

    def test_if_same_commercial_partner__payment_can_be_generated(self):
        receivable_1 = self._generate_receivable(100, partner=self.customer_a)
        receivable_2 = self._generate_receivable(200, partner=self.contact_a1)
        receivable_3 = self._generate_receivable(300, partner=self.contact_a2)

        receivables = receivable_1 | receivable_2 | receivable_3

        wizard = self._open_wizard(receivables)
        self._validate_wizard(wizard)

        for item in receivables:
            assert self._is_reconciled(item)

    def test_if_different_accounts__raise_error(self):
        account_2 = self.receivable_account.copy({'code': '111212'})
        receivable_1 = self._generate_receivable(100, account=self.receivable_account)
        receivable_2 = self._generate_receivable(200, account=account_2)

        with pytest.raises(UserError):
            self._open_wizard(receivable_1 | receivable_2)

    def test_if_different_currencies_accounts__raise_error(self):
        receivable_1 = self._generate_receivable(100)
        receivable_2 = self._generate_receivable(200, currency=self.env.ref('base.CAD'))

        with pytest.raises(UserError):
            self._open_wizard(receivable_1 | receivable_2)

    def test_multiple_lines_with_validation_errors(self):
        payable_1 = self._generate_receivable(100, account=self.payable_account)
        payable_2 = self._generate_receivable(200, account=self.payable_account)

        with pytest.raises(UserError):
            self._open_wizard(payable_1 | payable_2)


class TestPaymentInDifferentCurrency(PaymentWizardCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cad = cls.env.ref('base.CAD')
        cls.eur = cls.env.ref('base.EUR')

        cls.env['res.currency.rate'].search([]).unlink()
        cls._add_currency_rate(cls.cad, 2)
        cls._add_currency_rate(cls.eur, 3)

        cls.revenue_account.currency_id = cls.cad
        cls.payment_journal.currency_id = cls.eur

    @classmethod
    def _add_currency_rate(cls, currency, rate):
        cls.env['res.currency.rate'].create({
            'currency_id': currency.id,
            'rate': rate,
        })

    def test_payment_difference_with_payment_in_different_currency(self):
        move_1 = self._generate_receivable(100, amount_currency=200, currency=self.cad)
        move_2 = self._generate_receivable(200, amount_currency=600, currency=self.cad)

        wizard = self._open_wizard(move_1 | move_2)
        wizard.amount = 100
        wizard.currency_id = self.eur
        assert wizard.payment_difference == 1100  # (200 + 600) * 3 / 2 - 100

    def test_reconcile_difference_with_payment_in_different_currency(self):
        receivable = self._generate_receivable(300, amount_currency=600, currency=self.cad)

        wizard = self._open_wizard(receivable)
        wizard.amount = 100
        wizard.currency_id = self.eur
        wizard.payment_difference_handling = 'reconcile'
        wizard.writeoff_account_id = self.writeoff_account

        self._validate_wizard(wizard)
        assert self._is_reconciled(receivable)

    def test_open_difference_with_payment_in_different_currency(self):
        receivable = self._generate_receivable(300, amount_currency=600, currency=self.cad)

        wizard = self._open_wizard(receivable)
        wizard.amount = 150
        wizard.currency_id = self.eur

        self._validate_wizard(wizard)
        assert receivable.amount_residual == 250  # 300 - (150 / 3)
        assert receivable.amount_residual_currency == 500  # 600 - (150 * 2 / 3)
