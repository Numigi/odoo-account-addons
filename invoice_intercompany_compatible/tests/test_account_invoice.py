# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase, Form


class TestAccountInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create(
            {
                "name": "Company A",
            }
        )


        cls.company_b = cls.env["res.company"].create(
            {
                "name": "Company B",
            }
        )

        cls.bank_account_b = cls.env["res.partner.bank"].create(
            {
                "partner_id": cls.company_b.partner_id.id,
                "company_id": cls.company_b.id,
                "acc_number": "123456",
            }
        )

    def test_bank_account(self):
        invoice_obj = self.env["account.invoice"].with_context(
            default_type="out_invoice", default_company_id=self.company_a.id
        )
        with Form(invoice_obj) as form:
            form.company_id = self.company_b
            assert form.partner_bank_id == self.bank_account_b
