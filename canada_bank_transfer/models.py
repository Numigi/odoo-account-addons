# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from .transaction_types import TRANSACTION_TYPES, DEFAULT_TRANSACTION_TYPE


class Bank(models.Model):

    _inherit = 'res.bank'

    canada_institution = fields.Char(size=3, string='Institution Number')

    @api.constrains('canada_institution')
    def _check_canada_institution_is_3_digits(self):
        banks_with_institution = self.filtered(lambda b: b.canada_institution)
        for bank in banks_with_institution:
            if not bank.canada_institution.isdigit() or len(bank.canada_institution) != 3:
                raise ValidationError(_(
                    'The institution number must contain 3 digits. Got `{}`.'
                ).format(bank.canada_institution))


class BankAccount(models.Model):

    _inherit = 'res.partner.bank'

    canada_transit = fields.Char(size=5, string='Transit Number')

    @api.constrains('canada_transit')
    def _check_canada_transit_is_5_digits(self):
        accounts_with_transit = self.filtered(lambda b: b.canada_transit)
        for account in accounts_with_transit:
            if not account.canada_transit.isdigit() or len(account.canada_transit) != 5:
                raise ValidationError(_(
                    'The transit number must contain 5 digits. Got `{}`.'
                ).format(account.canada_transit))

    @property
    def formatted_canada_number(self):
        return '{transit} {institution} {account_number}'.format(
            transit=self.canada_transit or 'XXXXX',
            institution=self.bank_id.canada_institution or 'XXX',
            account_number=self.acc_number,
        )

    @api.multi
    def name_get(self):
        """Format the displayed name of canada accounts with the extra fields.

        The transit and institution number are added.

        If the transit or the institution number is missing, replace the number
        with a series of `X`. This allows to easily identify what field is missing.
        """
        canada_accounts = self.filtered(lambda a: a.canada_transit or a.bank_id.canada_institution)
        canada_accounts_result = [(a.id, a.formatted_canada_number) for a in canada_accounts]

        other_accounts = self - canada_accounts
        other_accounts_result = super(BankAccount, other_accounts).name_get()

        return canada_accounts_result + other_accounts_result

    @api.depends('acc_number')
    def _compute_sanitized_acc_number(self):
        """Add canada parts to the field sanitized_acc_number.

        This prevents the unique constraint from failling on sanitized_acc_number
        if 2 accounts with different transits have the same number.
        """
        canada_accounts = self.filtered(lambda a: a.canada_transit)
        for account in canada_accounts:
            account.sanitized_acc_number = account.formatted_canada_number

        other_accounts = self - canada_accounts
        super(BankAccount, other_accounts)._compute_sanitized_acc_number()


class AccountJournal(models.Model):

    _inherit = "account.journal"

    canada_transit = fields.Char(
        'Transit Number',
        size=5,
        related='bank_account_id.canada_transit',
        readonly=False,
    )

    eft_user_short_name = fields.Char(
        "EFT User Short Name",
        size=15,
        help="A short version of your company name. "
        "Must be composed of maximum 15 alphanumeric caracters."
    )

    eft_user_number = fields.Char(
        "EFT User Number",
        size=10,
        help="This number is attributed by your bank to identify your company. "
        "It is composed of 10 alphanumeric caracters."
    )

    eft_destination = fields.Char(
        "EFT Destination",
        size=5,
        help="Technical value of 5 digits used in the EFT file. "
        "It indicates the data processing center that will handle your tranfers. "
        "The value depends on the bank and the location of your company."
    )

    eft_enabled = fields.Boolean(compute='_compute_eft_enabled', store=True)

    @api.depends('outbound_payment_method_ids')
    def _compute_eft_enabled(self):
        eft_method = self.env.ref('canada_bank_transfer.payment_method_eft')
        for journal in self:
            journal.eft_enabled = (eft_method in journal.outbound_payment_method_ids)


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    eft_transaction_type = fields.Selection(
        TRANSACTION_TYPES,
        'EFT Transaction Type',
        default=DEFAULT_TRANSACTION_TYPE,
    )

    is_eft_payment = fields.Boolean(compute='_compute_is_eft_payment', store=True)

    @api.depends('payment_method_id')
    def _compute_is_eft_payment(self):
        eft_method = self.env.ref('canada_bank_transfer.payment_method_eft')
        for payment in self:
            payment.is_eft_payment = (payment.payment_method_id == eft_method)


class AccountPaymentWithEFTmartButton(models.Model):
    """Add fields required on payments to display the EFT smart button."""

    _inherit = 'account.payment'

    eft_ids = fields.Many2many(
        'account.eft',
        relation='account_eft_payment_rel',
        column1='payment_id',
        column2='eft_id',
        string='EFT',
    )

    eft_count = fields.Integer(compute='_compute_eft_count')

    def _compute_eft_count(self):
        for payment in self:
            payment.eft_count = len(payment.eft_ids)
