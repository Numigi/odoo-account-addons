# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestAccountPayment(AccountTestInvoicingCommon):
    def test_default_invoice_date(self):
        move = self.env["account.move"].create({"move_type": "in_invoice"})
        self.assertEqual(move.invoice_date, fields.Date.today())
        move = self.env["account.move"].create({"move_type": "out_invoice"})
        self.assertFalse(move.invoice_date)
