# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from ..transaction_types import TRANSACTION_TYPES, DEFAULT_TRANSACTION_TYPE
from odoo.exceptions import UserError


class AccountPayment(models.Model):

    _inherit = "account.payment"

    eft_ids = fields.Many2many(
        "account.eft",
        relation="account_eft_payment_rel",
        column1="payment_id",
        column2="eft_id",
        string="EFT",
        copy=False,
    )

    eft_count = fields.Integer(compute="_compute_eft_count")

    eft_transaction_type = fields.Selection(
        TRANSACTION_TYPES,
        "EFT Transaction Type",
        default=DEFAULT_TRANSACTION_TYPE,
    )

    is_eft_payment = fields.Boolean(
        compute="_compute_is_eft_payment", store=True)

    def _compute_eft_count(self):
        for payment in self:
            payment.eft_count = len(payment.eft_ids)

    @api.depends("payment_method_id")
    def _compute_is_eft_payment(self):
        """Compute the field is_eft_payment.

        raise_if_not_found=False is used because the field may be evaluated
        before the xml ID was loaded in the system.
        """
        eft_method = self.env.ref(
            "canada_bank_transfer.payment_method_eft", raise_if_not_found=False
        )
        for payment in self:
            payment.is_eft_payment = (
                eft_method and payment.payment_method_id == eft_method
            )

    def action_draft(self):
        for payment in self:
            if payment.eft_ids and payment.state in ['posted', 'sent', 'reconciled']:
                raise UserError(
                    _('You cannot cancel a payment linked to an Electronic Funds Transfer.'))
        super().action_draft()
