# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common

USER_SHORT_NAME = "YOUR COMPANY"
USER_NUMBER = "COMPANY001"
DESTINATION = "00610"


class EFTCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rbc = cls.env["res.bank"].create(
            {
                "name": "Royal Bank of Canada",
                "canada_institution": "003",
            }
        )

        cls.td = cls.env["res.bank"].create(
            {
                "name": "The Toronto-Dominion Bank",
                "canada_institution": "004",
            }
        )

        cls.nbc = cls.env["res.bank"].create(
            {
                "name": "National Bank of Canada",
                "canada_institution": "006",
            }
        )

        cls.nbc_account = cls.env["res.partner.bank"].create(
            {
                "bank_id": cls.nbc.id,
                "canada_transit": "10001",
                "acc_number": "1000001",
                "partner_id": cls.env.ref("base.main_partner").id,
            }
        )

        cls.eft_method = cls.env.ref("canada_bank_transfer.payment_method_eft")

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "NBC 10001 006 1000001",
                "type": "bank",
                "code": "NBC",
                "bank_account_id": cls.nbc_account.id,
                "currency_id": cls.env.ref("base.CAD").id,
                "eft_user_short_name": USER_SHORT_NAME,
                "eft_user_number": USER_NUMBER,
                "eft_destination": DESTINATION,
                "outbound_payment_method_ids": [(4, cls.eft_method.id)],
            }
        )

        cls.supplier_1 = cls.env["res.partner"].create(
            {"name": "Supplier 1"}
        )

        cls.td_account = cls.env["res.partner.bank"].create(
            {
                "bank_id": cls.td.id,
                "canada_transit": "20002",
                "acc_number": "2000002",
                "partner_id": cls.supplier_1.id,
            }
        )

        cls.supplier_2 = cls.env["res.partner"].create(
            {"name": "Supplier 2"}
        )

        cls.rbc_account = cls.env["res.partner.bank"].create(
            {
                "bank_id": cls.rbc.id,
                "canada_transit": "30003",
                "acc_number": "3000003",
                "partner_id": cls.supplier_2.id,
            }
        )

    @classmethod
    def generate_payment(cls, bank_account, amount):
        payment = cls.env["account.payment"].create(
            {
                "journal_id": cls.journal.id,
                "partner_id": bank_account.partner_id.id,
                "partner_bank_id": bank_account.id,
                "amount": amount,
                "payment_type": "outbound",
                "payment_method_id": cls.env.ref(
                    "canada_bank_transfer.payment_method_eft"
                ).id,
                "currency_id": cls.env.ref("base.CAD").id,
                "partner_type": "supplier",
                "eft_transaction_type": "450",
            }
        )
        payment.action_post()
        return payment
