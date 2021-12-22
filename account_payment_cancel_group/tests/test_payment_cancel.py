# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import AccessError


class TestPaymentCancel(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Test User',
            'email': 'test@test.com',
            'login': 'test@test.com',
            'groups_id': [
                (4, cls.env.ref('account.group_account_manager').id),
            ]
        })

        cls.journal = cls.env['account.journal'].create({
            'name': 'Test Bank Journal',
            'type': 'bank',
            'code': 'TEST',
        })

        cls.supplier = cls.env['res.partner'].create({'name': 'Supplier'})
        cls.payment = cls.env['account.payment'].create({
            'journal_id': cls.journal.id,
            'partner_id': cls.supplier.id,
            'amount': 100,
            'payment_type': 'outbound',
            'payment_method_id': cls.env.ref('account.account_payment_method_manual_out').id,
            'partner_type': 'supplier',
        })

    def test_if_not_member_of_group__action_draft_not_allowed(self):
        with pytest.raises(AccessError):
            self.payment.sudo(self.user).action_draft()

    def test_if_not_member_of_group__action_cancel_not_allowed(self):
        with pytest.raises(AccessError):
            self.payment.sudo(self.user).action_cancel()

    def test_if_member_of_group__user_allowed(self):
        self.user.groups_id |= self.env.ref('account_payment_cancel_group.group_cancel_payments')
        self.payment.sudo(self.user).action_draft()
        assert self.payment.state == 'draft'
        self.payment.sudo(self.user).action_cancel()
        assert self.payment.state == 'cancel'

    def test_call_method_with_empty_recordset(self):
        self.env["account.payment"].sudo(self.user).action_draft()
