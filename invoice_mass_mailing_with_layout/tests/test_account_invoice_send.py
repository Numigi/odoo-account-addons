# © 2022 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoices = cls.env["account.move"].search(
            [("move_type", "=", "out_invoice")])
        cls.template = cls.env.ref("account.email_template_edi_invoice")
        cls.template.auto_delete = False

    def test_send_multiple_invoices(self):
        wizard = self._create_wizard(self.invoices)
        wizard.send_and_print_action()

        email_1 = self._find_last_email(self.invoices[0])
        self._check_email_has_layout(email_1)

        email_2 = self._find_last_email(self.invoices[1])
        self._check_email_has_layout(email_2)

    def _check_email_has_layout(self, email):
        assert email
        assert "<table" in email.body_html

    def _create_wizard(self, invoices):
        wizard_obj = self.env["account.invoice.send"].with_context(
            active_ids=invoices.ids,
            active_model="account.move",
        )
        defaults = wizard_obj.default_get(list(wizard_obj._fields))
        wizard = wizard_obj.create(defaults)
        wizard.template_id = self.template
        wizard.invoice_ids = invoices
        wizard.is_email = True
        wizard._compute_composition_mode()
        return wizard

    def _find_last_email(self, invoice):
        return self.env["mail.mail"].search(
            [("model", "=", "account.move"), ("res_id", "=", invoice.id),],
            order="id desc",
            limit=1,
        )
