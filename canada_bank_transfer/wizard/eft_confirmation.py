# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from ..change_payment_date import change_payment_date


class EFTConfirmationWizard(models.TransientModel):

    _name = "account.eft.confirmation.wizard"
    _description = "EFT Confirmation Wizard"

    eft_id = fields.Many2one("account.eft")
    line_ids = fields.One2many("account.eft.confirmation.line", "wizard_id")

    @api.multi
    def action_validate(self):
        """Validate the EFT.

        * Update the state of the EFT to `done`.
        * Update the state of completed payments to sent.
        * Attach the EFT file to each completed payments.
        * Move the paiments not marked as `completed` to the `Failed Payments`
        * section in the form view of the EFT.
        * Creation journal Entries.
        """
        self.eft_id.state = "done"

        completed_payments = self.line_ids.filtered(lambda l: l.completed).mapped(
            "payment_id"
        )
        for payment in completed_payments:
            change_payment_date(payment, self.eft_id.payment_date)

        completed_payments.write({"state": "sent"})

        failed_payments = self.line_ids.filtered(lambda l: not l.completed).mapped(
            "payment_id"
        )

        self.eft_id.payment_ids = completed_payments
        self.eft_id.failed_payment_ids = failed_payments

        if self.eft_id.use_transit_account:
            self.eft_id.deposit_account_move_id = self._make_deposit_move()

        return True

    def _make_deposit_move(self):
        invoice_vals = self._prepare_account_move_values()
        move = self.env["account.move"].create(invoice_vals)
        move.post()
        self._reconcile_deposit_move(move)
        return move

    def _prepare_account_move_values(self):
        account_move_vals = {
            "ref": self.eft_id.name + _(" - Deposit"),
            "move_type": "entry",
            "date": fields.Date.today(),
            "journal_id": self.eft_id.journal_id.id,
            "line_ids": self._prepare_account_move_line_vals(),
        }
        return account_move_vals

    def _prepare_account_move_line_vals(self):
        vals_account_move_lines = []
        for line in self.line_ids.filtered(lambda line: line.completed):
            vals_account_move_lines.append((0, 0, self._get_payment_line_vals(line)))

        vals_account_move_lines.append((0, 0, self._get_counterpart_move_vals()))
        return vals_account_move_lines

    def _get_payment_line_vals(self, line):
        move_line = self._get_payment_move_line(line.payment_id)
        return {
            "partner_id": line.partner_id.id,
            "debit": move_line.credit,
            "account_id": move_line.account_id.id,
            "currency_id": move_line.currency_id.id,
            "amount_currency": -(move_line.amount_currency or 0),
            "name": line.payment_id.name + _(" - Deposit"),
        }

    def _get_counterpart_move_vals(self):
        return {
            "partner_id": self.eft_id.journal_id.company_id.partner_id.id,
            "credit": self._get_counterpart_move_amount(),
            "account_id": self.eft_id.journal_id.default_debit_account_id.id,
            "name": self.eft_id.name + _(" - Deposit"),
        }

    def _get_counterpart_move_amount(self):
        return sum(
            self._get_payment_move_line(l.payment_id).credit
            for l in self.line_ids
            if l.completed
        )

    def _reconcile_deposit_move(self, move):
        for line in move.line_ids.filtered("debit"):
            self._reconcile_deposit_move_line(line)

    def _reconcile_deposit_move_line(self, deposit_line):
        payment = self._get_payment_matching_deposit_line(deposit_line)
        payment_line = self._get_payment_move_line(payment)
        (payment_line | deposit_line).reconcile()

    def _get_payment_move_line(self, payment):
        return payment.move_line_ids.filtered("credit")[0]

    def _get_payment_matching_deposit_line(self, line):
        payments = self.mapped("line_ids.payment_id")
        return next(
            p for p in payments if p.name in line.name
        )


class EFTConfirmationLine(models.TransientModel):

    _name = "account.eft.confirmation.line"
    _description = "EFT Confirmation Line"

    wizard_id = fields.Many2one("account.eft.confirmation.wizard")
    payment_id = fields.Many2one("account.payment")
    payment_date = fields.Date(
        related="payment_id.payment_date",
        string="Payment Date",
    )
    name = fields.Char(
        related="payment_id.name",
        string="Name",
    )
    partner_id = fields.Many2one(
        related="payment_id.partner_id",
        string="Partner",
    )
    partner_bank_account_id = fields.Many2one(
        related="payment_id.partner_bank_account_id",
        string="Recipient Bank Account",
    )
    amount = fields.Monetary(
        related="payment_id.amount",
        string="Payment Amount",
    )
    currency_id = fields.Many2one(
        related="payment_id.currency_id",
    )
    completed = fields.Boolean(
        string="Completed",
        default=True,
    )
