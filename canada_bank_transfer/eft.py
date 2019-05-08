# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.account.models.account_payment import account_payment as Payment
from .generate_eft import generate_eft
from .payment_validation import (
    check_account_number_between_7_and_12_digits,
    check_all_payments_have_same_journal,
    check_bank_account_is_selected_on_payments,
    check_bank_is_selected_on_bank_accounts,
    check_institution_number_is_set_on_banks,
    check_payment_method_is_eft,
    check_payment_state_is_posted,
    check_transit_number_is_set_on_bank_accounts,
)


def auto_assign_bank_account_to_payments(payments: Payment) -> None:
    """Automatically assign a bank account to the given payments.

    If the partner on the payment has one bank account, then
    assign that account.

    Otherwise, do nothing. We let the user decide what destination
    bank account to use.
    """
    for payment in payments:
        partner_account = payment.partner_id.bank_ids
        if len(partner_account) == 1:
            payment.partner_bank_account_id = partner_account


class EFT(models.Model):

    _name = 'account.eft'
    _description = 'EFT'
    _inherit = 'mail.thread'
    _order = 'name desc'

    name = fields.Char('Name', compute='_compute_name', store=True)

    payment_date = fields.Date(
        'Payment Date', required=True,
        default=fields.Date.context_today,
        track_visibility='onchange')

    filename = fields.Char('File Name', readonly=True)

    content = fields.Text()
    content_binary = fields.Binary('File', readonly=True)

    payment_ids = fields.Many2many(
        comodel_name='account.payment',
        relation='account_eft_payment_rel',
        column1='eft_id',
        column2='payment_id',
        string='Payments',
        track_visibility='onchange')

    failed_payment_ids = fields.Many2many(
        comodel_name='account.payment',
        relation='account_eft_failed_payment_rel',
        column1='eft_id',
        column2='payment_id',
        string='Failed Payments',
        track_visibility='onchange')

    total = fields.Monetary('Total', compute='_compute_total')

    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=True,
        track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], readonly=True, default='draft', required=True, track_visibility='onchange')

    payment_notices_sent = fields.Boolean()

    def _compute_name(self):
        for eft in self:
            eft.name = "EFT{0:0>4}".format(eft.id) if eft.id else _("New EFT")

    @api.depends('payment_ids')
    def _compute_total(self):
        for eft in self:
            eft.total = sum(eft.payment_ids.mapped('amount'))

    @api.depends('payment_ids')
    def _compute_journal_id(self):
        for eft in self:
            eft.journal_id = eft.payment_ids[0].journal_id if eft.payment_ids else None

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for eft in self:
            eft.currency_id = eft.journal_id.currency_id or eft.journal_id.company_id.currency_id

    @api.model
    def create(self, vals):
        eft = super().create(vals)
        eft._compute_name()
        return eft

    @api.multi
    def unlink(self):
        validated_eft = self.filtered(lambda r: r.state != 'draft')
        if validated_eft:
            raise ValidationError(_('You may not delete an EFT that is not draft.'))
        return super().unlink()

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    def _check_payment_and_bank_accounts(self):
        check_payment_method_is_eft(self.payment_ids, self._context)
        check_payment_state_is_posted(self.payment_ids, self._context)
        check_bank_account_is_selected_on_payments(self.payment_ids, self._context)
        check_bank_is_selected_on_bank_accounts(self.payment_ids, self._context)
        check_transit_number_is_set_on_bank_accounts(self.payment_ids, self._context)
        check_institution_number_is_set_on_banks(self.payment_ids, self._context)
        check_account_number_between_7_and_12_digits(self.payment_ids, self._context)

    @api.multi
    def validate_payments(self):
        self._check_payment_and_bank_accounts()
        self.write({'state': 'ready'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                rec.payment_ids.write({'state': 'posted'})
        self.write({'state': 'cancelled'})

    @api.multi
    def action_done(self):
        wizard = self.env['account.eft.confirmation.wizard'].create({
            'eft_id': self.id,
        })
        for payment in self.payment_ids:
            wizard.line_ids |= self.env['account.eft.confirmation.line'].create({
                'payment_id': payment.id,
            })

        res = wizard.get_formview_action()
        res['target'] = 'new'
        return res

    @api.model
    def create_eft_from_payments(self, payments):
        check_payment_method_is_eft(payments, self._context)
        check_all_payments_have_same_journal(payments, self._context)
        check_payment_state_is_posted(payments, self._context)
        auto_assign_bank_account_to_payments(payments)

        eft = self.create({
            'state': 'draft',
            'journal_id': payments[0].journal_id.id,
            'payment_ids': [(6, 0, payments.ids)],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.eft',
            'view_mode': 'form',
            'target': 'current',
            'res_id': eft.id,
        }

    @api.multi
    def generate_eft_file(self):
        self._check_payment_and_bank_accounts()
        content = generate_eft(self.journal_id, self.payment_ids, self.id)
        self.write({
            'filename': "%s.txt" % self.name,
            'content': content,
            'content_binary': base64.encodestring(content.encode('utf-8')),
        })
        return True

    @api.multi
    def open_payment_notice_wizard(self):
        """Open the payment notice wizard.

        This wizard sends a notice to each payment recipient.

        Technical Note
        --------------
        The context variable {'active_id': False} is important.
        Otherwise, the ID of the EFT is passed to the wizard and causes an
        error related to multi-company rules of account.payment.
        """
        self.ensure_one()
        template = self.env.ref('canada_bank_transfer.payment_notice_email_template')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.payment',
                'active_ids': self.payment_ids.ids,
                'active_id': False,  # See technical note in docstring
                'default_composition_mode': 'mass_mail',
                'default_template_id': template.id,
                'default_use_template': True,
                'default_is_eft_payment_notice': True,
                'default_eft_id': self.id,
            }
        }
