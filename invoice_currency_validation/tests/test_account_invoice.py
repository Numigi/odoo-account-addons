# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestInvoiceValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.ref("base.USD")
        cls.currency_cad = cls.env.ref("base.CAD")
        cls.currency_eur = cls.env.ref("base.EUR")

        cls.company = cls.env["res.company"].create(
            {
                "name": "New Company",
                "currency_id": cls.company_currency.id,
            }
        )

        cls.env.user.company_ids |= cls.company
        cls.env.user.company_id = cls.company

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
            }
        )

        cls.payable_account = cls.env["account.account"].create(
            {
                "name": "Payable Account",
                "code": "1706",
                "reconcile": True,
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )

        cls.payable_account_cad = cls.env["account.account"].create(
            {
                "name": "Payable Account CAD",
                "code": "1707",
                "reconcile": True,
                "company_id": cls.company.id,
                "currency_id": cls.currency_cad.id,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )

        cls.expense_account = cls.env["account.account"].create(
            {
                "name": "Expenses Account",
                "code": "1708",
                "company_id": cls.company.id,
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Journal",
                "type": "purchase",
                "code": "PJUSD",
                "company_id": cls.company.id,
            }
        )

        cls.journal_cad = cls.env["account.journal"].create(
            {
                "name": "Journal",
                "type": "purchase",
                "code": "PJCAD",
                "currency_id": cls.currency_cad.id,
                "company_id": cls.company.id,
            }
        )

        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Journal",
                "type": "sale",
                "code": "SJCAD",
                "company_id": cls.company.id,
            }
        )

        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
                "property_account_payable_id": cls.payable_account.id,
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.supplier.id,
                "journal_id": cls.journal.id,
                "currency_id": cls.company_currency.id,
                "company_id": cls.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "product_id": cls.product.id,
                            "account_id": cls.expense_account.id,
                            "price_unit": 1000,
                        },
                    )
                ],
                "move_type": "in_invoice",
            }
        )
        cls.payable_line = cls.invoice.line_ids.filtered(
            lambda l: l.account_id.internal_type == "payable"
        )

    def _validate_invoice(self):
        self.invoice.action_post()

    def test_journal_without_currency_and_account_without_currency(self):
        self._validate_invoice()
        self.assertEqual(self.invoice.state, "posted")

    def test_invoice_with_currency_and_journal_without_currency(self):
        self.invoice.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_journal_and_invoice_with_different_currencies(self):
        self.journal.currency_id = self.currency_cad
        with self.assertRaises(UserError):
            self._validate_invoice()

    def test_account_and_invoice_with_different_currencies(self):
        self.payable_line.write(
            {
                "currency_id": self.currency_cad.id,
                "amount_currency": -1500,
                "account_id": self.payable_account_cad.id,
            }
        )
        with self.assertRaises(UserError):
            self._validate_invoice()
