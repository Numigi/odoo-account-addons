# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from ..transaction_types import TRANSACTION_TYPES, DEFAULT_TRANSACTION_TYPE
from odoo.exceptions import ValidationError, UserError


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
            if payment.eft_ids and payment.state == 'posted':
                raise UserError(
                    _("You cannot reset to draft a payment linked to "
                      "an Electronic Funds Transfer."))
        super().action_draft()

    def _prepare_move_line_default_vals(self ,  write_off_line_vals=None):
        vals = super()._prepare_move_line_default_vals( write_off_line_vals)
        if self.journal_id.use_transit_account and self.payment_method_id == self.env.ref("canada_bank_transfer.payment_method_eft"):
            if not self.journal_id.transit_account:
                 raise ValidationError(
                     _("You must choose an Transit Account in Journal %s.") % self.journal_id.name)
            else:
                 vals[0].update({"account_id": self.journal_id.transit_account.id})
        return vals


    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in (
                    self.journal_id.default_account_id,
                    self.journal_id.payment_debit_account_id,
                    self.journal_id.payment_credit_account_id,
                    self.journal_id.transit_account,
            ):
                liquidity_lines += line
            elif line.account_id.internal_type in ('receivable', 'payable') or line.account_id == line.company_id.transfer_account_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines