# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


@ddt
class TestAccountInvoice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.ref('base.USD')
        cls.currency_cad = cls.env.ref('base.CAD')
        cls.currency_eur = cls.env.ref('base.EUR')

        cls.company = cls.env['res.company'].create({
            'name': 'New Company',
            'currency_id': cls.company_currency.id,
        })

        cls.env.user.company_ids |= cls.company
        cls.env.user.company_id = cls.company

        cls.product = cls.env['product.product'].create({
            'name': 'Product',
        })

        cls.account_1 = cls.env['account.account'].create({
            'name': 'Payable Account',
            'code': '1706',
            'reconcile': True,
            'company_id': cls.company.id,
            'user_type_id': cls.env.ref(
                'account.data_account_type_payable').id,
        })

        cls.account_2 = cls.env['account.account'].create({
            'name': 'Expenses Account',
            'code': '1708',
            'company_id': cls.company.id,
            'user_type_id': cls.env.ref(
                'account.data_account_type_expenses').id,
        })

        cls.journal = cls.env['account.journal'].create({
            'name': 'Journal',
            'type': 'purchase',
            'code': 'PJUSD',
            'company_id': cls.company.id,
        })

        cls.journal_cad = cls.env['account.journal'].create({
            'name': 'Journal',
            'type': 'purchase',
            'code': 'PJCAD',
            'currency_id': cls.currency_cad.id,
            'company_id': cls.company.id,
        })

        cls.sale_journal = cls.env['account.journal'].create({
            'name': 'Journal',
            'type': 'sale',
            'code': 'SJCAD',
            'company_id': cls.company.id,
        })

        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier',
            'property_account_payable_id': cls.account_2.id,
        })

        cls.line = cls.env['account.invoice.line'].create({
            'name': 'Line',
            'product_id': cls.product.id,
            'account_id': cls.account_2.id,
            'price_unit': 1000,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.supplier.id,
            'journal_id': cls.journal.id,
            'account_id': cls.account_1.id,
            'currency_id': cls.company_currency.id,
            'company_id': cls.company.id,
            'invoice_line_ids': [(4, cls.line.id)],
            'type': 'in_invoice',
        })

    def _validate_invoice(self):
        self.invoice.action_invoice_open()

    def test_journal_without_currency_and_account_without_currency(self):
        self._validate_invoice()
        self.assertEqual(self.invoice.state, 'open')

    def test_invoice_with_currency_and_journal_without_currency(self):
        self.invoice.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_journal_with_currency_and_account_without_currency(self):
        self.journal.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_journal_without_currency_and_account_with_currency(self):
        self.account_1.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_journal_and_account_with_different_currencies(self):
        self.journal.currency_id = self.currency_cad
        self.account_1.currency_id = self.currency_eur
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_journal_and_invoice_with_different_currencies(self):
        self.journal.currency_id = self.currency_cad
        self.account_1.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def _trigger_onchange(self):
        self.invoice._onchange_currency_set_journal()

    def test_onchange_currency_with_foreign_currency(self):
        self.invoice.currency_id = self.currency_cad
        self._trigger_onchange()
        assert self.invoice.journal_id == self.journal_cad

    def test_onchange_currency_with_company_currency(self):
        self.invoice.currency_id = self.company_currency
        self.invoice.journal_id = self.journal_cad
        self._trigger_onchange()
        assert self.invoice.journal_id == self.journal

    def test_onchange_currency__journal_with_lower_sequence_selected(self):
        self.journal.sequence = 1
        other_journal = self.journal.copy({
            'name': 'Other Journal',
            'sequence': 0,
            'code': 'PJUSD2',
        })
        self._trigger_onchange()
        assert self.invoice.journal_id == other_journal

    @data(
        ('in_invoice', 'purchase'),
        ('in_refund', 'purchase'),
        ('out_invoice', 'sale'),
        ('out_refund', 'sale'),
    )
    @unpack
    def test_onchange_currency__correct_journal_type_selected(self, invoice_type, journal_type):
        self.invoice.type = invoice_type
        self._trigger_onchange()
        assert self.invoice.journal_id.type == journal_type
