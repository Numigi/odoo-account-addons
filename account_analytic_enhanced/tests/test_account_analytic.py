# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestAccountAnalytic(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'Customer Task',
            'email': 'customer@task.com',
            'customer': True,
        })

        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'My Analytic Account',
            'partner_id': cls.partner.id,
        })

        cls.analytic_line = cls.env['account.analytic.line'].create({
            'name': 'My Analytic line',
            'account_id': cls.analytic_account.id})

    def test_account_analytic_stays_active(self):
        self.analytic_account.toggle_active()
        self.project.write({'active': True})
        assert not self.analytic_account.active
