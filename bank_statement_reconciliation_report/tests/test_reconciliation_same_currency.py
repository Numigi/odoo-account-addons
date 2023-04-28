# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestReconciliation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Prepare Users and Bank Statements."""
        super(TestReconciliation, cls).setUpClass()

        currency_cad_id = cls.env.ref("base.CAD")
        company = cls.env.ref('base.main_company')

        company.currency_id = currency_cad_id.id
        # create journal
        cls.journal = cls.env["account.journal"].create(
            {"name": "My Bank", "type": "bank", "code": "MBK",
                "currency_id": currency_cad_id.id}
        )
        # create customer
        cls.client = cls.env["res.partner"].create({"name": "Client"})
        # create supplier
        cls.supplier = cls.env["res.partner"].create({"name": "Supllier"})
        # add customer payment
        cls.cli_pay_1 = cls.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": cls.client.id,
                "amount": 500,
                "journal_id": cls.journal.id,
                "payment_date": "2022-03-01",
                "payment_method_id": cls.env.ref("account.account_payment_method_manual_in").id,
            }
        )
        cls.cli_pay_1.post()
        # add customer payment
        cls.cli_pay_2 = cls.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": cls.client.id,
                "amount": 300,
                "journal_id": cls.journal.id,
                "payment_date": "2022-03-03",
                "payment_method_id": cls.env.ref("account.account_payment_method_manual_in").id,
            }
        )
        cls.cli_pay_2.post()
        # add supplier payment
        cls.sup_pay_1 = cls.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": cls.supplier.id,
                "amount": 500,
                "journal_id": cls.journal.id,
                "payment_date": "2022-03-01",
                "payment_method_id": cls.env.ref("account.account_payment_method_manual_out").id,
            }
        )
        cls.sup_pay_1.post()
        # create bank statement
        cls.bank_statement_1 = cls.env["account.bank.statement"].create(
            {
                "journal_id": cls.journal.id,
                "date": "2022-03-30",
                "balance_start": 200,
                "balance_end_real": 600,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2022-03-25",
                            "amount": 400,
                            "name": "Transaction test",
                        },
                    )
                ],
            }
        )

    def test_conciliation_wizard_same_currency(self):
        bank_statement_1 = self.bank_statement_1
        bank_statement_1.button_bank_conciliation()
        conciliation = bank_statement_1.conciliation_id
        self.assertEqual(conciliation.journal_id.currency_id,
                         conciliation.journal_id.company_id.currency_id)
        self.assertEqual(conciliation.total_inbound, 800.0)
        self.assertEqual(conciliation.total_outbound, 500.0)
