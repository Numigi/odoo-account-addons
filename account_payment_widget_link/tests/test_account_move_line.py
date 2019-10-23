# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo.tests.common import SavepointCase


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
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner',
            'property_account_payable_id': cls.payable.id,
        })
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
        cls.invoice_move_line = cls.invoice.move_id.line_ids.filtered(
            lambda l: l.account_id == cls.payable
        )

        cls.bank_journal = cls.env['account.journal'].create({
            'name': 'Test Bank Journal',
            'type': 'bank',
            'code': 'TEST',
        })
        cls.payment = cls.env['account.payment'].create({
            'journal_id': cls.bank_journal.id,
            'partner_id': cls.partner.id,
            'amount': 100,
            'payment_method_id': cls.env.ref('account.account_payment_method_manual_out').id,
            'partner_type': 'supplier',
            'payment_type': 'outbound',
        })
        cls.payment.post()
        cls.payment_move_line = cls.payment.move_line_ids.filtered(
            lambda l: l.account_id == cls.payable
        )

    def test_if_invoice_origin__invoice_form_view_opened(self):
        res = self.invoice_move_line.get_payment_widget_link_action()
        assert res['res_id'] == self.invoice.id
        assert res['res_model'] == 'account.invoice'

    def test_if_payment_origin__payment_form_view_opened(self):
        res = self.payment_move_line.get_payment_widget_link_action()
        assert res['res_id'] == self.payment.id
        assert res['res_model'] == 'account.payment'

    def test_if_move_line_has_no_origin__move_line_form_view_opened(self):
        self.invoice_move_line.invoice_id = False
        res = self.invoice_move_line.get_payment_widget_link_action()
        assert res['res_id'] == self.invoice_move_line.move_id.id
        assert res['res_model'] == 'account.move'
