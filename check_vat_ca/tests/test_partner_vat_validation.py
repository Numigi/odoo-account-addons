# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestPartnerVatValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_check_vat_canada(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Canadian Partner",
                "country_id": self.env.ref("base.ca").id,
            }
        )
        # The constrainte will not be raised even if the vat does't contain "CA"
        partner.vat = '123456789'
