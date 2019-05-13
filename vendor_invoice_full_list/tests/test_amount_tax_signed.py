# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
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
        cls.tax_amount = 100
        cls.tax = cls.env['account.tax'].create({
            'name': 'Test',
            'account_id': cls.payable.id,
            'amount_type': 'fixed',
            'amount': cls.tax_amount,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'journal_id': cls.journal.id,
            'account_id': cls.payable.id,
            'invoice_line_ids': [(0, 0, {
                'name': '/',
                'account_id': cls.expense.id,
                'price_unit': 1000,
                'invoice_line_tax_ids': [(4, cls.tax.id)],
            })],
            'type': 'out_invoice',
        })
        cls.invoice.action_invoice_open()

    def test_if_out_invoice__then_tax_amount_is_positive(self):
        assert self.invoice.amount_tax_signed == self.tax_amount

    def test_if_out_refund__then_tax_amount_is_negative(self):
        self.type = 'out_refund'
        assert self.invoice.amount_tax_signed == self.tax_amount

    def test_if_in_invoice__then_tax_amount_is_positive(self):
        self.type = 'in_invoice'
        assert self.invoice.amount_tax_signed == self.tax_amount

    def test_if_in_refund__then_tax_amount_is_negative(self):
        self.type = 'in_refund'
        assert self.invoice.amount_tax_signed == self.tax_amount
