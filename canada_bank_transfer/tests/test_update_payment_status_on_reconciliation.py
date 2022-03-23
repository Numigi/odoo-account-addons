# © 2022 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .test_etf_transit_account import TestTransitMoveCase


class TestPaymentStatusReconciled(TestTransitMoveCase):
    def test_payment_reconciled__status_reconciled(self):
        wizard = self._open_confirmation_wizard_etf()
        wizard.action_validate()
        assert self.eft.mapped("payment_ids.state") == ["reconciled", "reconciled"]
