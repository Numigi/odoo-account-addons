# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestAccountInvoice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoice, cls).setUpClass()
        cls.payable = cls.env['account.account'].create({
            'name': 'Payable',
            'code': '210110',
            'reconcile': True,
            'user_type_id': cls.env.ref('account.data_account_type_payable').id,
        })
        cls.expense = cls.env['account.account'].create({
            'name': 'Expenses',
            'code': '510110',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'Journal',
            'type': 'sale',
            'code': 'SAJ',
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Partner'})
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'journal_id': cls.journal.id,
            'account_id': cls.payable.id,
            'invoice_line_ids': [(0, 0, {
                'name': '/',
                'account_id': cls.expense.id,
                'price_unit': 1000,
            })],
            'type': 'in_invoice',
        })
        cls.invoice.action_invoice_open()

    def _open_refund_wizard(self, invoice):
        return (
            self.env['account.invoice.refund']
            .with_context(active_ids=[invoice.id])
            .create({})
        )

    def test_supplier_refund__if_accounting_date_prior__raise_error(self):
        wizard = self._open_refund_wizard(self.invoice)
        wizard.date = datetime.now().date() - timedelta(1)
        with pytest.raises(ValidationError):
            wizard.compute_refund('cancel')

    def test_supplier_refund__if_invoice_date_prior__raise_error(self):
        wizard = self._open_refund_wizard(self.invoice)
        wizard.date_invoice = datetime.now().date() - timedelta(1)
        with pytest.raises(ValidationError):
            wizard.compute_refund('cancel')

    def test_supplier_refund__if_date_same_as_invoice__refund_generated(self):
        wizard = self._open_refund_wizard(self.invoice)
        wizard.compute_refund('cancel')
        assert self.invoice.state == 'paid'

    def test_customer_refund__if_accounting_date_prior__raise_error(self):
        self.invoice.type = 'out_invoice'
        wizard = self._open_refund_wizard(self.invoice)
        wizard.date = datetime.now().date() - timedelta(1)
        with pytest.raises(ValidationError):
            wizard.compute_refund('cancel')

    def test_customer_refund__if_date_prior__raise_error(self):
        self.invoice.type = 'out_invoice'
        wizard = self._open_refund_wizard(self.invoice)
        wizard.date_invoice = datetime.now().date() - timedelta(1)
        with pytest.raises(ValidationError):
            wizard.compute_refund('cancel')

    def test_customer_refund__if_date_same_as_invoice__refund_generated(self):
        self.invoice.type = 'out_invoice'
        wizard = self._open_refund_wizard(self.invoice)
        wizard.compute_refund('cancel')
        assert self.invoice.refund_invoice_ids.state == 'open'
