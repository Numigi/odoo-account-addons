# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _
from odoo.exceptions import ValidationError


def check_payment_method_is_eft(payments, context):
    """Check that the given payments have the EFT payment method selected."""
    payments_with_wrong_method = payments.filtered(lambda p: p.payment_method_id.code != 'eft')
    if payments_with_wrong_method:
        raise ValidationError(_(
            "The following payments can not be used to generate an EFT "
            "because they do not have the `EFT` payment method selected:\n\n{}"
        ).format(', '.join(payments_with_wrong_method.mapped('display_name'))))


def check_all_payments_have_same_journal(payments, context):
    """Check that the given payments have the same accounting journal."""
    journals = payments.mapped('journal_id')
    if len(journals) != 1:
        raise ValidationError(_(
            "In order to generate the EFT "
            "all payments must have the same accounting journal. "
            "Some payments selected have different journals:\n\n{}"
        ).format(', '.join(journals.mapped('display_name'))))


def check_payment_state_is_posted(payments, context):
    """Check that the given payments are posted."""
    payments_with_wrong_state = payments.filtered(lambda p: p.state != 'posted')
    if payments_with_wrong_state:
        raise ValidationError(_(
            "The following payments can not be used to generate an EFT "
            "because they are not at the `posted` state:\n\n{}"
        ).format(', '.join(payments_with_wrong_state.mapped('display_name'))))


def check_bank_account_is_selected_on_payments(payments, context):
    payments_with_no_account = payments.filtered(lambda p: not p.partner_bank_id)
    if payments_with_no_account:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "no bank account is selected on the following payments:\n\n{}"
        ).format(', '.join(payments_with_no_account.mapped('display_name'))))


def check_bank_is_selected_on_bank_accounts(payments, context):
    accounts_with_no_bank = (
        payments.mapped('partner_bank_id')
        .filtered(lambda a: not a.bank_id)
    )
    if accounts_with_no_bank:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "no bank is selected on the following bank accounts:\n\n{}"
        ).format(', '.join(accounts_with_no_bank.mapped('display_name'))))


def check_transit_number_is_set_on_bank_accounts(payments, context):
    accounts_with_no_transit = (
        payments.mapped('partner_bank_id')
        .filtered(lambda a: not a.canada_transit)
    )
    if accounts_with_no_transit:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "the transit number is missing on the following bank accounts:\n\n{}"
        ).format(', '.join(accounts_with_no_transit.mapped('display_name'))))


def check_institution_number_is_set_on_banks(payments, context):
    banks_with_no_institution = (
        payments.mapped('partner_bank_id.bank_id')
        .filtered(lambda b: not b.canada_institution)
    )
    if banks_with_no_institution:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "the institution number is missing on the following banks:\n\n{}"
        ).format(', '.join(banks_with_no_institution.mapped('display_name'))))


def check_account_number_between_7_and_12_digits(payments, context):
    accounts_with_wrong_chars = (
        payments.mapped('partner_bank_id')
        .filtered(lambda a: not (a.acc_number or '').isdigit())
    )
    if accounts_with_wrong_chars:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "the following bank accounts have a number with non-digit caracters:\n\n{}"
        ).format(', '.join(accounts_with_wrong_chars.mapped('display_name'))))

    accounts_with_more_12_digits = (
        payments.mapped('partner_bank_id')
        .filtered(lambda a: len(a.acc_number or '') > 12)
    )
    if accounts_with_more_12_digits:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "the following bank accounts have more than 12 digits:\n\n{}"
        ).format(', '.join(accounts_with_more_12_digits.mapped('display_name'))))

    accounts_with_less_7_digits = (
        payments.mapped('partner_bank_id')
        .filtered(lambda a: len(a.acc_number or '') < 7)
    )
    if accounts_with_less_7_digits:
        raise ValidationError(_(
            "The EFT can not be generated because "
            "the following bank accounts have less than 7 digits:\n\n{}"
        ).format(', '.join(accounts_with_less_7_digits.mapped('display_name'))))
