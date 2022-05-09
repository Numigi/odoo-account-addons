# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo.tests.common import SavepointCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestReconciliation(SavepointCase):

    def test_conciliation_wizard(cls):
        # create journal
        cls.journal = cls.env["account.journal"].create({
            "name": "My Bank", "type": "bank", "code": "MBK"
        })
        # create customer
        cls.client = cls.env["res.partner"].create({
            "name": "Client"
        })
        # create supplier
        cls.supplier = cls.env["res.partner"].create({
            "name": "Supllier"
        })
        # add customer payment
        cls.cli_pay_1 = cls.env["account.payment"].create({
            "payment_type": "inbound",
            "partner_type":"customer",
            "partner_id": cls.client.id,
            "amount": 500,
            "journal_id": cls.journal.id,
            "payment_date": "2022-03-01",
            "payment_method_id":cls.env.ref('account.account_payment_method_manual_in').id,
        })
        cls.cli_pay_1.post()
        # add customer payment
        cls.cli_pay_2 = cls.env["account.payment"].create({
            "payment_type": "inbound",
            "partner_type": "customer",
            "partner_id": cls.client.id,
            "amount": 300,
            "journal_id": cls.journal.id,
            "payment_date": "2022-03-03",
            "payment_method_id": cls.env.ref('account.account_payment_method_manual_in').id,
        })
        cls.cli_pay_2.post()
        # add supplier payment
        cls.sup_pay_1 = cls.env["account.payment"].create({
            "payment_type": "outbound",
            "partner_type": "supplier",
            "partner_id": cls.supplier.id,
            "amount": 500,
            "journal_id": cls.journal.id,
            "payment_date": "2022-03-01",
            "payment_method_id": cls.env.ref('account.account_payment_method_manual_out').id,
        })
        cls.sup_pay_1.post()
        # create bank statement
        cls.bank_statement_1 = cls.env['account.bank.statement'].create({
            "journal_id":cls.journal.id,
            "date": "2022-03-30",
            "balance_start": 200,
            "balance_end_real": 600,
            "line_ids": [(0,0,{
                "date":"2022-03-25",
                "amount":400,
                "name":"Transaction test"
            })]
        })
        cls.assertEqual(cls.bank_statement_1.conciliation_id.total_inbound, 800.0)
        cls.assertEqual(cls.bank_statement_1.conciliation_id.total_outbound, 500.0)
