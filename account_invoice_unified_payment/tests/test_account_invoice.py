# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime, timedelta
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAccountInvoice(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cad = cls.env.ref("base.CAD")
        cls.payable = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "210110",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
            }
        )
        cls.payable_cad = cls.env["account.account"].create(
            {
                "name": "Payable CAD",
                "code": "210120",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "currency_id": cls.cad.id,
            }
        )
        cls.expense = cls.env["account.account"].create(
            {
                "name": "Expenses",
                "code": "510110",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Journal",
                "type": "sale",
                "code": "SAJ",
            }
        )
        cls.journal_cad = cls.env["account.journal"].create(
            {
                "name": "Journal CAD",
                "type": "sale",
                "code": "SCAD",
                "currency_id": cls.cad.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.invoice = cls._make_invoice(1000)
        cls.refund = cls._make_invoice(400, type="in_refund")
        cls.invoice.action_invoice_open()
        cls.refund.action_invoice_open()

    @classmethod
    def _make_invoice(cls, amount, **kwargs):
        defaults = {
            "partner_id": cls.partner.id,
            "journal_id": cls.journal.id,
            "account_id": cls.payable.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "/",
                        "account_id": cls.expense.id,
                        "price_unit": amount,
                    },
                )
            ],
            "type": "in_invoice",
        }
        return cls.env["account.invoice"].create(
            {
                **defaults,
                **kwargs,
            }
        )

    def test_basic_case(self):
        action = (self.invoice | self.refund).reconcile_and_open_payment()
        assert action["res_model"] == "account.register.payments"
        assert action["context"]["active_model"] == "account.invoice"
        assert action["context"]["active_ids"] == [self.invoice.id]

        assert self.refund.state == "paid"
        assert self.invoice.residual == 600  # 1000 - 400

    def test_refund_higher_than_invoice(self):
        refund_2 = self._make_invoice(1100, type="in_refund")
        refund_2.action_invoice_open()

        with pytest.raises(ValidationError):
            action = (self.invoice | refund_2).reconcile_and_open_payment()

    def test_refund_in_different_currency(self):
        refund_2 = self._make_invoice(
            400,
            type="in_refund",
            currency_id=self.cad.id,
            journal_id=self.journal_cad.id,
            account_id=self.payable_cad.id,
        )
        refund_2.action_invoice_open()

        with pytest.raises(ValidationError):
            (self.invoice | refund_2).reconcile_and_open_payment()

    def test_refund_with_different_commercial_partner(self):
        refund_2 = self._make_invoice(
            400,
            type="in_refund",
            partner_id=self.partner.copy().id,
        )
        refund_2.action_invoice_open()

        with pytest.raises(ValidationError):
            (self.invoice | refund_2).reconcile_and_open_payment()

    def test_refund_with_different_account(self):
        refund_2 = self._make_invoice(
            400,
            type="in_refund",
            account_id=self.payable.copy({"code": "222222"}).id,
        )
        refund_2.action_invoice_open()

        with pytest.raises(ValidationError):
            (self.invoice | refund_2).reconcile_and_open_payment()

    def test_draft_invoice(self):
        invoice = self._make_invoice(100)

        with pytest.raises(ValidationError):
            invoice.reconcile_and_open_payment()
