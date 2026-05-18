# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestBankStatementCheckPartnerMapping(SavepointCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up the necessary records for testing check partner mappings.
        """
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test Supplier 2"})

        # Locate or create the check printing payment method FIRST
        cls.payment_method_check = cls.env["account.payment.method"].search(
            [("code", "=", "check_printing"), ("payment_type", "=", "outbound")], limit=1
        )
        if not cls.payment_method_check:
            cls.payment_method_check = cls.env["account.payment.method"].create({
                "name": "Check Printing",
                "code": "check_printing",
                "payment_type": "outbound",
            })

        # Journal A with a specific check format AND the payment method allowed
        cls.journal_a = cls.env["account.journal"].create({
            "name": "Bank Journal A",
            "type": "bank",
            "code": "BKA",
            "check_format": "CHK - {check_number}",
            "outbound_payment_method_ids": [(4, cls.payment_method_check.id)],
        })

        # Journal B with another check format AND the payment method allowed
        cls.journal_b = cls.env["account.journal"].create({
            "name": "Bank Journal B",
            "type": "bank",
            "code": "BKB",
            "check_format": "CHQ-{check_number}-B",
            "outbound_payment_method_ids": [(4, cls.payment_method_check.id)],
        })

    def _create_payment(self, partner, journal, check_number):
        """
        Helper method to create an outbound check payment.
        """
        payment = self.env["account.payment"].create({
            "partner_id": partner.id,
            "amount": 100.0,
            "payment_type": "outbound",
            "partner_type": "supplier",
            "journal_id": journal.id,
            "payment_method_id": self.payment_method_check.id,
        })

        if check_number:
            # Force assigning the check number after creation to trigger the write method
            payment.check_number = check_number

        return payment

    def test_01_payment_mapping_lifecycle(self):
        """
        Test the lifecycle of a check payment regarding its mapping creation and archiving.
        """
        payment = self._create_payment(self.partner, self.journal_a, "1001")

        # 1. Post the payment and verify mapping creation
        payment.action_post()

        assert len(payment.check_mapping_ids) == 1
        mapping = payment.check_mapping_ids[0]
        assert mapping.label == "CHK - 1001"
        assert mapping.journal_id == self.journal_a
        assert mapping.partner_id == self.partner
        assert mapping.active

        # 2. Cancel the payment and verify the mapping is archived
        payment.action_cancel()
        assert not mapping.active

        # 3. Reset to draft and verify it remains archived
        payment.action_draft()
        assert not mapping.active

    def test_02_bank_statement_recuperate_by_payment_ref(self):
        """
        Test partner recuperation using the standard payment_ref field.
        """
        payment = self._create_payment(self.partner, self.journal_a, "1002")
        payment.action_post()

        statement = self.env["account.bank.statement"].create({
            "name": "Statement 1",
            "journal_id": self.journal_a.id,
            "line_ids": [(0, 0, {
                "payment_ref": "CHK - 1002",
                "amount": -100.0,
            })]
        })

        statement.button_recuperate_partners()

        assert statement.line_ids[0].partner_id == self.partner

    def test_03_bank_statement_recuperate_by_ref(self):
        """
        Test partner recuperation falling back to the ref field when payment_ref is incomplete.
        """
        payment = self._create_payment(self.partner_2, self.journal_b, "2001")
        payment.action_post()

        statement = self.env["account.bank.statement"].create({
            "name": "Statement 2",
            "journal_id": self.journal_b.id,
            "line_ids": [(0, 0, {
                "payment_ref": "Generic Bank Text",
                "ref": "CHQ-2001-B",  # The actual check info is here
                "amount": -100.0,
            })]
        })

        statement.button_recuperate_partners()

        assert statement.line_ids[0].partner_id == self.partner_2

    def test_04_bank_statement_journal_isolation(self):
        """
        Test that a mapping generated for journal A does not apply to journal B.
        """
        payment = self._create_payment(self.partner, self.journal_a, "3001")
        payment.action_post()

        # Create a statement on journal B with the exact label matching journal A's check
        statement = self.env["account.bank.statement"].create({
            "name": "Statement 3",
            "journal_id": self.journal_b.id,
            "line_ids": [(0, 0, {
                "payment_ref": "CHK - 3001",
                "amount": -100.0,
            })]
        })

        statement.button_recuperate_partners()

        # Partner should NOT be recuperated because the journal isolates the rule
        assert not statement.line_ids[0].partner_id

    def test_05_payment_without_check_number(self):
        """
        Test that no mapping rule is created if the payment has no check number.
        """
        payment = self._create_payment(self.partner, self.journal_a, False)
        payment.action_post()

        assert len(payment.check_mapping_ids) == 0
