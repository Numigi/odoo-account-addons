# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestAccountInvoice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoice, cls).setUpClass()

        cls.currency_cad = cls.env.ref('base.CAD')
        cls.currency_eur = cls.env.ref('base.EUR')

        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
        })

        cls.account = cls.env['account.account'].create({
            'name': 'Account',
            'code': '1706',
            'user_type_id': cls.env.ref(
                'account.data_account_type_expenses').id,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'Journal',
            'type': 'bank',
            'code': 'JR1717',
        })

        cls.line = cls.env['account.invoice.line'].create({
            'name': 'Line',
            'product_id': cls.product.id,
            'account_id': cls.account.id,
            'price_unit': 1000,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.supplier.id,
            'journal_id': cls.journal.id,
            'account_id': cls.account.id,
            'currency_id': cls.currency_eur.id,
            'invoice_line_ids': [(4, cls.line.id)],
        })

    def test_01_journal_with_currency_and_account_without_currency(self):
        self.journal.write({'currency_id': self.currency_cad.id})
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()

    def test_02_journal_without_currency_and_account_with_currency(self):
        self.account.write({'currency_id': self.currency_cad.id})
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()

    def test_03_journal_and_account_with_different_currencies(self):
        self.journal.write({'currency_id': self.currency_cad.id})
        self.account.write({'currency_id': self.currency_eur.id})
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()

    def test_04_journal_and_invoice_with_different_currencies(self):
        self.journal.write({'currency_id': self.currency_cad.id})
        self.account.write({'currency_id': self.currency_cad.id})
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()
