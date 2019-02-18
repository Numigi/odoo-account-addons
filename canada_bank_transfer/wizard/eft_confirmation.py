# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from ..change_payment_date import change_payment_date


class EFTConfirmationWizard(models.TransientModel):

    _name = 'account.eft.confirmation.wizard'
    _description = 'EFT Confirmation Wizard'

    eft_id = fields.Many2one('account.eft')
    line_ids = fields.One2many('account.eft.confirmation.line', 'wizard_id')

    @api.multi
    def action_validate(self):
        """Validate the EFT.

        * Update the state of the EFT to `done`.
        * Update the state of completed payments to sent.
        * Attach the EFT file to each completed payments.
        * Move the paiments not marked as `completed` to the `Failed Payments`
        * section in the form view of the EFT.
        """
        self.eft_id.state = 'done'

        completed_payments = self.line_ids.filtered(lambda l: l.completed).mapped('payment_id')
        for payment in completed_payments:
            change_payment_date(payment, self.eft_id.payment_date)

        completed_payments.write({'state': 'sent'})

        failed_payments = self.line_ids.filtered(lambda l: not l.completed).mapped('payment_id')

        self.eft_id.payment_ids = completed_payments
        self.eft_id.failed_payment_ids = failed_payments

        return True


class EFTConfirmationLine(models.TransientModel):

    _name = 'account.eft.confirmation.line'
    _description = 'EFT Confirmation Line'

    wizard_id = fields.Many2one('account.eft.confirmation.wizard')
    payment_id = fields.Many2one('account.payment')
    payment_date = fields.Date(
        related='payment_id.payment_date',
        string="Payment Date",
    )
    name = fields.Char(
        related='payment_id.name',
        string="Name",
    )
    partner_id = fields.Many2one(
        related='payment_id.partner_id',
        string="Partner",
    )
    partner_bank_account_id = fields.Many2one(
        related='payment_id.partner_bank_account_id',
        string="Recipient Bank Account",
    )
    amount = fields.Monetary(
        related='payment_id.amount',
        string="Payment Amount",
    )
    currency_id = fields.Many2one(
        related='payment_id.currency_id',
    )
    completed = fields.Boolean(
        string='Completed',
        default=True,
    )
