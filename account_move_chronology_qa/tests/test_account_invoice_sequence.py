# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.addons.account_invoice_constraint_chronology.tests import (
    test_account_invoice_constraint_chronology as taicc,
)

TestAccountInvoiceConstraintChronology = taicc.TestAccountInvoiceConstraintChronology


class TestAccountInvoiceSequence(TestAccountInvoiceConstraintChronology):
    def setUp(self):
        super(TestAccountInvoiceSequence, self).setUp()
        self.AccountAccount = self.env["account.account"]
        self.account_data = self.env.ref("account.data_account_type_revenue")
        self.account_tag_operating = self.env.ref("account.account_tag_operating")
        self.account = self.AccountAccount.create(
            {
                "code": "X2023",
                "name": "Temp Sale Account - (numigi test)",
                "user_type_id": self.account_data.id,
                "tag_ids": [(6, 0, {self.account_tag_operating.id})],
            }
        )

        self.partner_demo = self.env["res.partner"].create(
            {
                "name": "Numigi Partner Demo",
            }
        )
        self.user2 = self.env["res.users"].create(
            {
                "login": "demo2",
                "password": "demo2",
                "partner_id": self.partner_demo.id,
                "groups_id": [
                    (6, 0, [self.env.ref("account.group_account_manager").id])
                ],
            }
        )
        self.product_a = self.env["product.product"].create({"name": "p1"})

    def test_01_readonly_check_chronology(self):
        view = self.env.ref("account.view_account_journal_form")

        form = Form(self.env["account.journal"].with_user(self.user2), view=view)

        form.name = "Numigi Journal Test"
        form.type = "general"
        form.default_account_id = self.account
        form.code = "JNR01"
        form.check_chronology = True
        form1 = form.save()

        # field must be visible if not type sale or purchase
        self.assertEqual(
            form._get_modifier(field="check_chronology", modifier="invisible"),
            True,
            msg=None,
        )

        # if change type other than sale and purchase,
        # check_chronology will be set to False
        form1._onchange_type()
        self.assertEqual(form1.check_chronology, False)

        # if type is sale
        form.type = "sale"
        form.save()
        self.assertEqual(
            form._get_modifier(field="check_chronology", modifier="invisible"),
            False,
            msg=None,
        )

        # if type is purchase and test onchange
        form.type = "purchase"
        form.save()
        self.assertEqual(
            form._get_modifier(field="check_chronology", modifier="invisible"),
            False,
            msg=None,
        )

    def test_02_invoice_chronology_issue(self):
        journal = (
            self.env["account.journal"]
            .with_user(self.user2)
            .create(
                {
                    "name": "Numigi Journal Test",
                    "type": "sale",
                    "default_account_id": self.account.id,
                    "code": "JNR01",
                    "check_chronology": True,
                }
            )
        )
        # older_conflicting_invoices
        # ==========================
        # testing conflict for two draft invoices created
        invoice1 = (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-08-15",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )

        invoice2 = (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-09-01",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )
        with self.assertRaises(UserError) as exc:
            invoice2.action_post()

        error_msg = (
            "Chronology conflict: A conflicting draft invoice dated before "
            "09/01/2023 exists, please validate it first."
        )
        self.assertEqual(error_msg, str(exc.exception))

        # newer_conflicting_invoices
        # ==========================
        # testing chronology for draft invoice created
        # before an invoice already posted
        invoice1.action_post()

        invoice3 = (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-08-10",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )
        with self.assertRaises(UserError) as exc:
            invoice3.action_post()

        error_msg = (
            "Chronology conflict: A conflicting validated invoice dated "
            "after 08/10/2023 exists."
        )
        self.assertEqual(error_msg, str(exc.exception))

        # Last scenario test
        journal1 = (
            self.env["account.journal"]
            .with_user(self.user2)
            .create(
                {
                    "name": "Numigi Journal Test A",
                    "type": "sale",
                    "default_account_id": self.account.id,
                    "code": "JNR01",
                    "check_chronology": False,
                }
            )
        )

        (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-07-20",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )

        invoice5 = (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-08-23",
                    "journal_id": journal1.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )

        invoice6 = (
            self.env["account.move"]
            .with_user(self.user2)
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner_demo.id,
                    "invoice_date": "2023-09-04",
                    "journal_id": journal1.id,
                    "invoice_line_ids": [
                        (0, 0, {"product_id": self.product_a.id, "price_unit": 1000.0})
                    ],
                }
            )
        )

        invoice6.action_post()

        with self.assertRaises(UserError) as exc:
            invoice5.write({"journal_id": journal.id})
            invoice5.action_post()

        error_msg = (
            "Chronology conflict: A conflicting draft invoice dated "
            "before 08/23/2023 exists, please validate it first."
        )
        self.assertEqual(error_msg, str(exc.exception))
