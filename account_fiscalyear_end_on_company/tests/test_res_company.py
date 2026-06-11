# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResCompany(TransactionCase):
    """Test suite for the fiscal year end fields on the res.company model."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment and initialize a test company."""
        super().setUpClass()
        # Initialize a dedicated company for testing purposes
        cls.test_company = cls.env["res.company"].create(
            {
                "name": "Numigi Test Company",
            }
        )

    def test_fiscalyear_end_fields_assignment(self):
        """Ensure fiscal year fields are correctly assigned and persisted."""
        # Assign December 31st as the end of the fiscal year
        self.test_company.write(
            {
                "fiscalyear_last_day": 31,
                "fiscalyear_last_month": "12",
            }
        )

        # Verify the day assignment
        self.assertEqual(
            self.test_company.fiscalyear_last_day,
            31,
            "The fiscalyear_last_day should be exactly 31.",
        )

        # Verify the month assignment
        self.assertEqual(
            self.test_company.fiscalyear_last_month,
            "12",
            "The fiscalyear_last_month should be precisely December ('12').",
        )
