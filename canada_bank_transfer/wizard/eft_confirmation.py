# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from ..change_payment_date import change_payment_date


class EFTConfirmationWizard(models.TransientModel):

    _name = "account.eft.confirmation.wizard"
    _description = "EFT Confirmation Wizard"

    eft_id = fields.Many2one("account.eft")
    line_ids = fields.One2many("account.eft.confirmation.line", "wizard_id")

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

        completed_payments.mark_as_sent()

        failed_payments = self.line_ids.filtered(lambda l: not l.completed).mapped(
            "payment_id"
        )

        self.eft_id.payment_ids = completed_payments
        self.eft_id.failed_payment_ids = failed_payments

        # Creation of journal Entries
        if self.eft_id.use_transit_account:
            invoice_vals = self._prepare_account_move_values()
            deposit_account_move = self.env["account.move"].create(invoice_vals)
            deposit_account_move.post()
            self.eft_id.deposit_account_move_id = deposit_account_move.id
        
        # Update payment move lines accounts when using transit account
        self._update_payment_move_accounts()
        
        # Create EFTGROUP journal entry when using transit account
        if self.eft_id.use_transit_account:
            self._create_eftgroup_journal_entry()
        
        return True

    def _prepare_account_move_values(self):
        """Prepare values of EFT Entries."""
        account_move_vals = {
            "ref": self.eft_id.name + _(" - Deposit"),
            "move_type": "entry",
            "date": fields.Date.today(),
            "journal_id": self.eft_id.journal_id.id,
            "line_ids": self._prepare_account_move_line_vals(),
        }
        return account_move_vals

    def _prepare_account_move_line_vals(self):
        """Prepare line values of EFT Entries."""
        vals_account_move_lines = []
        for line in self.line_ids.filtered(lambda line: line.completed):
            vals_account_move_lines.append((0, 0, self._get_payment_line_vals(line)))

        vals_account_move_lines.append(
            (
                0,
                0,
                {
                    "partner_id": self.eft_id.journal_id.company_id.partner_id.id,
                    "credit": sum(
                        self.line_ids.filtered(lambda line: line.completed).mapped(
                            "amount"
                        )
                    ),
                    "account_id": self.eft_id.journal_id.payment_credit_account_id.id,
                    "name": self.eft_id.name + _(" - Deposit"),
                },
            )
        )
        return vals_account_move_lines

    def _get_payment_line_vals(self, line):
        """Prepare line values of EFT Entries from Payments."""
        return {
            "partner_id": line.partner_id.id,
            "debit": line.amount,
            "account_id": self.eft_id.journal_id.transit_account.id,
            "name": self.eft_id.name + _(" - Deposit"),
        }

    def _update_payment_move_accounts(self):
        """Update payment move line accounts when using transit account."""
        # Check if use_transit_account is activated
        if not self.eft_id.use_transit_account:
            return
        
        journal = self.eft_id.journal_id
        payment_credit_account = journal.payment_credit_account_id
        transit_account = journal.transit_account
        
        # Validate that both accounts are set
        if not payment_credit_account or not transit_account:
            return
        
        # Browse all payments in payment_ids
        for payment in self.eft_id.payment_ids:
            # Browse the move_id related to the payment
            if not payment.move_id:
                continue
            
            move = payment.move_id
            
            # Cancel the move before making changes to avoid validation errors
            if move.state == 'posted':
                move.button_cancel()
            
            # Browse the line_ids in move_id and update accounts
            # Use context to skip payment synchronization validation
            for move_line in move.line_ids:
                # Replace account if it matches payment_credit_account_id
                if move_line.account_id == payment_credit_account:
                    move_line.with_context(
                        skip_account_move_synchronization=True,
                        check_move_validity=False
                    ).write({
                        'account_id': transit_account.id
                    })
            
            # Re-post the move after making changes
            if move.state == 'cancel':
                move.button_draft()
                move.action_post()

    def _create_eftgroup_journal_entry(self):
        """Create EFTGROUP journal entry for transit account movements."""
        journal = self.eft_id.journal_id
        transit_account = journal.transit_account
        
        # Prepare the move lines
        line_vals = []
        total_debit = 0.0
        
        # Create debit lines from each payment's transit account credit lines
        for payment in self.eft_id.payment_ids:
            if not payment.move_id:
                continue
                
            # Find credit lines with transit account in payment moves
            for move_line in payment.move_id.line_ids:
                if (move_line.account_id == transit_account and 
                    move_line.credit > 0):
                    
                    # Create corresponding debit line
                    line_vals.append((0, 0, {
                        'account_id': transit_account.id,
                        'partner_id': payment.partner_id.id,
                        'debit': move_line.credit,
                        'credit': 0.0,
                        'name': 'EFTGROUP - ' + payment.name,
                    }))
                    total_debit += move_line.credit
        
        # Add outstanding account credit line for balancing
        if total_debit > 0:
            outstanding_account = journal.default_account_id
            line_vals.append((0, 0, {
                'account_id': outstanding_account.id,
                'partner_id': journal.company_id.partner_id.id,
                'debit': 0.0,
                'credit': total_debit,
                'name': 'EFTGROUP - Bank Outstanding',
            }))
            
            # Create the journal entry
            eftgroup_move = self.env['account.move'].create({
                'ref': 'EFTGROUP',
                'journal_id': journal.id,
                'date': fields.Date.today(),
                'move_type': 'entry',
                'line_ids': line_vals,
            })
            
            # Post the journal entry
            eftgroup_move.action_post()
            
            return eftgroup_move
        
        return False


class EFTConfirmationLine(models.TransientModel):

    _name = "account.eft.confirmation.line"
    _description = "EFT Confirmation Line"

    wizard_id = fields.Many2one("account.eft.confirmation.wizard")
    payment_id = fields.Many2one("account.payment")
    payment_date = fields.Date(
        related="payment_id.date",
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
        related="payment_id.partner_bank_id",
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
