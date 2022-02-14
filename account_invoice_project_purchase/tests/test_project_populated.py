# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields
from odoo.tests.common import SavepointCase


class TestPopulatedProject(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_account = cls.env["account.analytic.account"].create({
            "name": "Analytic Account"
        })
        cls.project = cls.env["project.project"].create({
            "name": "Project",
            "analytic_account_id": cls.analytic_account.id
        })
        cls.product = cls.env["product.product"].create({
            "name": "Test Product",
            "type": "service",
            "purchase_method": "receive",
        })
        cls.vendor = cls.env["res.partner"].create({
            "name": "Test Vendor",
            "supplier": True,
        })
        cls.purchase = cls.env["purchase.order"].create({
            "partner_id": cls.vendor.id
        })
        cls.purchase_line = cls.env["purchase.order.line"].create({
            "name": cls.product.name,
            "product_id": cls.product.id,
            "project_id": cls.project.id,
            "account_analytic_id": cls.analytic_account.id,
            "product_qty": 1,
            "order_id": cls.purchase.id,
            "date_planned": fields.Datetime.now(),
            "product_uom": cls.product.uom_id.id,
            "price_unit": 1,
            "qty_received": 1,
        })

    @classmethod
    def _generate_vendor_bill_from_po(cls):
        cls.purchase.button_confirm()
        account_invoice_env = cls.env["account.invoice"]
        bill = account_invoice_env.new({
            "purchase_id": cls.purchase.id,
            "journal_id":
                cls.env["account.journal"].search(
                    [("type", "=", "purchase")], limit=1
                ).id,
            "type": "in_invoice",
        })
        bill.purchase_order_change()
        bill_data = bill._convert_to_write(bill._cache)
        return account_invoice_env.create(bill_data)

    def test_pol_onchange_project_id(self):
        purchase_order_line = self.env["purchase.order.line"].new({
            "project_id": self.project.id,
        })
        purchase_order_line._onchange_project()
        self.assertTrue(
            self.analytic_account == purchase_order_line.account_analytic_id
        )

    def test_invoice_line_onchange_project_id(self):
        invoice_line = self.env["account.invoice.line"].new({
            "project_id": self.project.id,
        })
        invoice_line._onchange_project()
        self.assertTrue(
            self.analytic_account == invoice_line.account_analytic_id
        )

    def test_bill_from_po_populate_project_id(self):
        self.purchase.button_confirm()
        bill = self.env["account.invoice"].new({
            "purchase_id": self.purchase.id,
        })
        bill.purchase_order_change()
        purchase_project = self.purchase.order_line[0].project_id
        bill_project = bill.invoice_line_ids[0].project_id
        self.assertTrue(bill_project == purchase_project)

    def test_bill_set_auto_complete_populate_project_id(self):
        bill = self._generate_vendor_bill_from_po()
        # Make Invoice status of purchase to "to invoice" status to have Bill Union
        bill.invoice_line_ids.write({"quantity": 0})
        bill_union = self.env["purchase.bill.union"].search([
            ("purchase_order_id", "=", self.purchase.id)]
        )
        auto_complete_bill = self.env["account.invoice"].new({
            "vendor_bill_purchase_id": bill_union.id,
        })
        auto_complete_bill._onchange_bill_purchase_order()
        auto_complete_bill.purchase_order_change()
        bill_project = bill.invoice_line_ids[0].project_id
        auto_bill_project = auto_complete_bill.invoice_line_ids[0].project_id
        self.assertTrue(bill_project == auto_bill_project)

    def test_credit_note_from_bill_populate_project_and_analytic_account(self):
        bill = self._generate_vendor_bill_from_po()
        bill.action_invoice_open()
        refund_wizard = \
            self.env["account.invoice.refund"].with_context(
                active_id=bill.id, active_ids=bill.ids
            ).create({
                "description": "Test",
            })
        refund_wizard.invoice_refund()
        refund_invoice = \
            self.env["account.invoice"].search([("refund_invoice_id", "=", bill.id)])
        bill_project = bill.invoice_line_ids[0].project_id
        bill_analytic_account = bill.invoice_line_ids[0].account_analytic_id
        refund_project = refund_invoice.invoice_line_ids[0].project_id
        refund_analytic_account = refund_invoice.invoice_line_ids[0].account_analytic_id
        self.assertTrue(
            bill_project == refund_project
            and bill_analytic_account == refund_analytic_account
        )
