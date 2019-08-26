# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class TestAccountMoveAccess(SavepointCase):

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

        cls.journal = cls.env['account.journal'].search([], limit=1)
        cls.accounts = cls.env['account.account'].search([])

        cls.move = cls.env['account.move'].create({
            'journal_id': cls.journal.id,
            'line_ids': [
                (0, 0, {
                    'account_id': cls.accounts[0].id,
                    'name': '/',
                    'debit': 100,
                }),
                (0, 0, {
                    'account_id': cls.accounts[1].id,
                    'name': '/',
                    'credit': 100,
                })
            ]
        })
        cls.line_1 = cls.move.line_ids[0]
        cls.line_2 = cls.move.line_ids[1]

    def test_if_user_unauthorized__raise_error(self):
        with pytest.raises(AccessError):
            self.env['account.move.line'].sudo(self.user).check_extended_security_all()

    def test_if_user_authorized__error_not_raised(self):
        self.user.groups_id |= self.env.ref('account.group_account_invoice')
        self.env['account.move.line'].sudo(self.user).check_extended_security_all()

    def test_if_user_unauthorized__search_domain_restrained(self):
        domain = self.env['account.move.line'].sudo(self.user).get_extended_security_domain()
        lines = self.env['account.move.line'].search(domain)
        assert len(lines) == 0

    def test_if_user_authorized__search_domain_not_restrained(self):
        self.user.groups_id |= self.env.ref('account.group_account_invoice')
        domain = self.env['account.move.line'].sudo(self.user).get_extended_security_domain()
        lines = self.env['account.move.line'].search(domain)
        assert self.line_1 in lines
        assert self.line_2 in lines
