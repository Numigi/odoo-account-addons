# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestReconciliationDifferentCurrency(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Prepare Users and Bank Statements."""
        super(TestReconciliationDifferentCurrency, cls).setUpClass()

        # define currency to company
        currency_usd_id = cls.env.ref("base.USD")
        currency_cad_id = cls.env.ref("base.CAD")
        company = cls.env.ref('base.main_company')

        company.currency_id = currency_cad_id.id

        # create journal
        cls.dollar_journal = cls.env["account.journal"].create(
            {"name": "My Bank", "type": "bank", "code": "MBK",
                "currency_id": currency_usd_id.id}
        )
        # create customer/supplier account
        account_type_rcv = cls.env['account.account.type'].create(
            {'name': 'RCV type', 'type': 'receivable'})
        customer_account = cls.env["account.account"].create(
            {"code": "usd_acc", "user_type_id": account_type_rcv.id, "name": "115100 USD CUSTOMER ACC",
                "currency_id": currency_usd_id.id, "reconcile": True}
        )
        account_type_pbl = cls.env['account.account.type'].create(
            {'name': 'PBL type', 'type': 'payable'})
        supplier_account = cls.env["account.account"].create(
            {"code": "usd_acc1", "user_type_id": account_type_pbl.id, "name": "115100 USD SUPPLIER ACC",
                "currency_id": currency_usd_id.id, "reconcile": True}
        )
        # create customer/supplier
        cls.customer_supplier = cls.env["res.partner"].create({
            "name": "Customer / Supplier",
            "customer": True, "supplier": True,
            "property_account_receivable_id": customer_account.id,
            "property_account_payable_id": supplier_account.id
        })

        # add customer payment
        cls.cli_pay_1 = cls.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": cls.customer_supplier.id,
                "currency_id": currency_usd_id.id,
                "amount": 1000,
                "journal_id": cls.dollar_journal.id,
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
                "partner_id": cls.customer_supplier.id,
                "currency_id": currency_usd_id.id,
                "amount": 1000,
                "journal_id": cls.dollar_journal.id,
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
                "partner_id": cls.customer_supplier.id,
                "currency_id": currency_usd_id.id,
                "amount": 1000,
                "journal_id": cls.dollar_journal.id,
                "payment_date": "2022-03-01",
                "payment_method_id": cls.env.ref("account.account_payment_method_manual_out").id,
            }
        )
        cls.sup_pay_1.post()
        # add supplier payment
        cls.sup_pay_2 = cls.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": cls.customer_supplier.id,
                "currency_id": currency_usd_id.id,
                "amount": 1000,
                "journal_id": cls.dollar_journal.id,
                "payment_date": "2022-03-03",
                "payment_method_id": cls.env.ref("account.account_payment_method_manual_out").id,
            }
        )
        cls.sup_pay_2.post()
        # create bank statement
        cls.bank_statement_1 = cls.env["account.bank.statement"].create(
            {
                "journal_id": cls.dollar_journal.id,
                "date": "2022-03-03",
                "balance_start": 0,
                "balance_end_real": 2000,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2022-03-01",
                            "amount": 1000,
                            "name": "Transaction test",
                        },
                        0,
                        0,
                        {
                            "date": "2022-03-03",
                            "amount": -1000,
                            "name": "Transaction test",
                        }
                    )
                ],
            }
        )

    def test_conciliation_wizard_different_currency(self):
        bank_statement_1 = self.bank_statement_1
        bank_statement_1.button_bank_conciliation()
        conciliation = bank_statement_1.conciliation_id
        self.assertNotEqual(conciliation.journal_id.currency_id,
                            conciliation.journal_id.company_id.currency_id)
        self.assertEqual(conciliation.total_inbound, 2000.0)
        self.assertEqual(conciliation.total_outbound, 2000.0)
        self.assertEqual(conciliation.conciliation_balance, 2000.0)
        self.assertEqual(conciliation.account_balance, 0)
