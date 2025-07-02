# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, _

class AccountMove(models.Model):
    _inherit = "account.move"

    cr_auto_debit = fields.Boolean(string="Auto Debit?")

    def action_post(self):
        """ Override action_post to trigger auto debit payment when the invoice is posted. """
        res = super().action_post()

        for invoice in self:
            if invoice.cr_auto_debit:
                provide = self.env['payment.provider'].search([
                    ('code', 'ilike', 'Stripe'),
                ], limit=1)
                saved_token = self.env['payment.token'].search([
                    ('partner_id', '=', invoice.partner_id.id),
                    ('provider_id', '=', provide.id),
                    ('active', '=', True)
                ], limit=1)

                if saved_token:
                    payment = invoice._process_auto_debit_payment(saved_token)
                    if payment and payment.state == 'posted':
                        invoice.payment_state = 'paid'
                    else:
                        self._handle_payment_failure(invoice)
                # else:#No action required if no token
                #     self._handle_payment_failure(invoice)
                #     invoice.state = 'draft'
        return res

    def _process_auto_debit_payment(self, saved_token):
        """ Process automatic payment using the saved payment token. """
        try:
            stripe_provider =self.env['payment.provider'].search([
                    ('code', 'ilike', 'Stripe'),
                ], limit=1)

            if not stripe_provider or not stripe_provider.payment_method_ids:
                self._handle_payment_failure(self)

            stripe_journal = stripe_provider.journal_id
            stripe_payment_method = self.env['account.payment.method.line'].search([
                ('name', 'ilike', 'Stripe')
            ], limit=1)

            payment_vals = {
                'amount': self.amount_total,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'journal_id': stripe_journal.id,
                'payment_type': 'inbound',
                'payment_method_line_id': stripe_payment_method.id,
                'payment_reference': self.name,
                'payment_token_id': saved_token.id,
            }
            payment = self.env['account.payment'].create(payment_vals)
            payment.action_post()
            if payment and payment.state == 'posted':

                move_lines = self.line_ids.filtered(
                    lambda line: line.account_id.account_type == 'asset_receivable' and not line.reconciled
                )
                payment_lines = payment.move_id.line_ids.filtered(
                    lambda line: line.account_id.account_type == 'asset_receivable'
                )

                (move_lines + payment_lines).reconcile()
                transaction = self.env['payment.transaction'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('provider_id', '=', stripe_provider.id)
                ], limit=1)

                if transaction:
                    self.transaction_ids = [(4, transaction.id)]

            return payment
        except Exception as e:
            self._handle_payment_failure(self)
            return False

    def _handle_payment_failure(self, invoice):
        """
        Handle payment failure by logging the error, notifying the customer, and marking the invoice.
        """
        error_message = _("Auto-debit payment failed for invoice %s.", invoice.name)
        invoice.message_post(body=error_message)


        if invoice.partner_id.email:
            mail_values = {
                'subject': _("Payment Failed for Invoice %s" % invoice.name),
                'email_from': invoice.company_id.email or self.env.user.email,
                'email_to': invoice.partner_id.email,
                'body_html': """
                    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                        <p>Dear %s,</p>
                        <p>We regret to inform you that we were unable to process the auto-debit payment for your invoice <strong>%s</strong>.</p>
                        <p><strong>Invoice Details:</strong></p>
                        <ul>
                            <li><strong>Invoice Number:</strong> %s</li>
                            <li><strong>Amount Due:</strong> %s %s</li>
                            <li><strong>Due Date:</strong> %s</li>
                        </ul>
                        <p>Please update your payment method and try again. If you need assistance, feel free to contact us at <a href="mailto:%s">%s</a>.</p>
                        <p>Thank you for your understanding.</p>
                        <p>Best regards,<br/>%s</p>
                    </div>
                """ % (
                    invoice.partner_id.name,
                    invoice.name,
                    invoice.name,
                    invoice.amount_total,
                    invoice.currency_id.symbol,
                    invoice.invoice_date_due or _("N/A"),
                    invoice.company_id.email or self.env.user.email,
                    invoice.company_id.email or self.env.user.email,
                    invoice.company_id.name,
                ),
            }

            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

        invoice.write({'payment_state': 'not_paid',})
