# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class TestInvoiceAccess(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'My User',
            'login': 'testinvoice@example.com',
            'email': 'testinvoice@example.com',
            'groups_id': [
                (4, cls.env.ref('purchase.group_purchase_user').id),
                (4, cls.env.ref('sales_team.group_sale_salesman').id),
            ],
        })

    def test_if_user_unauthorized__on_create__raise_error(self):
        with pytest.raises(AccessError):
            self.env['account.invoice'].sudo(self.user).check_extended_security_create()

    def test_if_user_authorized__on_create__error_not_raised(self):
        self.user.groups_id |= self.env.ref('invoice_write_access.group_invoice')
        self.env['account.invoice'].sudo(self.user).check_extended_security_create()

    def test_if_user_unauthorized__on_write__raise_error(self):
        with pytest.raises(AccessError):
            self.env['account.invoice'].sudo(self.user).check_extended_security_write()

    def test_if_user_authorized__on_write__error_not_raised(self):
        self.user.groups_id |= self.env.ref('invoice_write_access.group_invoice')
        self.env['account.invoice'].sudo(self.user).check_extended_security_write()

    def test_if_user_unauthorized__on_unlink__raise_error(self):
        with pytest.raises(AccessError):
            self.env['account.invoice'].sudo(self.user).check_extended_security_unlink()

    def test_if_user_authorized__on_unlink__error_not_raised(self):
        self.user.groups_id |= self.env.ref('invoice_write_access.group_invoice')
        self.env['account.invoice'].sudo(self.user).check_extended_security_unlink()
