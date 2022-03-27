# © 2022 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .test_etf_transit_account import TestTransitMoveCase


class TestPaymentStatusUnreconciled(TestPaymentStatusReconciled):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payments.unreconcile()

    def _test_payment_unreconciled__status_sent(self):
        assert self.eft.mapped("payment_ids.state") == ["sent", "sent"]
