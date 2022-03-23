# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import math
import re
from unidecode import unidecode
from datetime import date
from odoo import _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round
from .transaction_types import DEFAULT_TRANSACTION_TYPE

AUTHORIZED_ASCII_CHARS = (" ", ".")


def _remove_accents_and_special_caracters(value):
    """Remove accents and special caracters from the given string."""
    value_with_no_accents = unidecode(value)
    return re.sub(r"[^a-zA-Z0-9,.\s]", "_", value_with_no_accents)


def _justify_right_with_zeros(value: object, text_length):
    """Format the given value with a left padding of zeros (justified to the right).

    :param value: the value to format.
    :param text_length: the total length of the returned string.
    """
    return "{0:0>{length}}".format(value, length=text_length)


def _justify_left_with_blanks(value: object, text_length):
    """Format the given value with a right padding of blanks (justified to the left).

    :param value: the value to format.
    :param text_length: the total length of the returned string.
    """
    return "{0: <{length}}".format(value, length=text_length)


def _format_julian_date(date_: date):
    """Format the given date as Julian date (0AAJJJ)."""
    timetuple = date_.timetuple()
    year = str(timetuple.tm_year)[-2:]
    day = str(timetuple.tm_yday).zfill(3)
    return "0{}{}".format(year, day)


def _verify_file_number(file_number, context):
    if not (1 <= file_number <= 9999):
        raise ValidationError(
            _("Expected an EFT file number between 1 and 9999. Got `{}`.").format(
                file_number
            )
        )


def _format_file_number(file_number):
    return _justify_right_with_zeros(str(file_number), 4)


def _verify_user_number(user_number, context):
    if not user_number or len(user_number) != 10:
        raise ValidationError(
            _("Expected a bank user number with 10 caracters. Got `{}`.").format(
                user_number
            )
        )


def _verify_destination_code(destination, context):
    if not destination or len(destination) != 5 or not destination.isdigit():
        raise ValidationError(
            _("Expected a destination code with 5 digits. Got `{}`.").format(
                destination
            )
        )


def _verify_currency_code(currency_code, context):
    if len(currency_code) != 3:
        raise ValidationError(
            _("Expected a currency name with 3 caracters. Got `{}`.").format(
                currency_code
            )
        )


def format_header(journal, file_number):
    """Format the header of an EFT file.

    :param currency: the bank journal.

    :param file_number: the sequence number of the EFT file

        Must be an integer between 1 and 9999.
        It is incremented after every EFT file.
    """
    context = journal._context

    currency_code = journal.currency_id.name or journal.company_id.currency_id.name

    _verify_user_number(journal.eft_user_number, context)
    _verify_file_number(file_number, context)
    _verify_currency_code(currency_code, context)
    _verify_destination_code(journal.eft_destination, context)

    return (
        "A000000001{user_number}{file_number}{create_date}{destination}"
        "{blank_20}"
        "{currency_code}"
        "{blank_1406}".format(
            user_number=journal.eft_user_number,
            file_number=_format_file_number(file_number),
            create_date=_format_julian_date(date.today()),
            destination=journal.eft_destination,
            blank_20=" " * 20,
            currency_code=currency_code,
            blank_1406=" " * 1406,
        )
    )


def _format_sequence_number(sequence_number):
    return _justify_right_with_zeros(str(sequence_number), 9)


def _verify_institution_number(institution_number, context):
    if not institution_number or len(institution_number) != 3:
        raise ValidationError(
            _("Expected an institution name with 3 caracters. Got `{}`.").format(
                institution_number
            )
        )

    if not institution_number.isdigit():
        raise ValidationError(
            _("The institution number `{}` must contain only digits.").format(number)
        )


def _verify_transit(transit, context):
    if not transit or len(transit) != 5:
        raise ValidationError(
            _("Expected a transit number with 5 caracters. Got `{}`.").format(transit)
        )

    if not transit.isdigit():
        raise ValidationError(
            _("The transit number `{}` must contain only digits.").format(number)
        )


def _verify_account_number(number, context):
    if not number.isdigit():
        raise ValidationError(
            _("The account number `{}` must contain only digits.").format(number)
        )

    if not (7 <= len(number) <= 12):
        raise ValidationError(
            _("The account number `{}` must contain between 7 and 12 digits.").format(
                number
            )
        )


def _format_account_number(number):
    return _justify_left_with_blanks(number, 12)


def _verify_user_short_name(user_short_name, context):
    if not user_short_name or len(user_short_name) > 15:
        raise ValidationError(
            _(
                "Expected a user short name between 1 and 15 caracters. Got `{}`."
            ).format(user_short_name)
        )


def _format_user_short_name(user_short_name):
    user_short_name_sanitized = _remove_accents_and_special_caracters(user_short_name)
    return _justify_left_with_blanks(user_short_name_sanitized.upper(), 15)


def _verify_user_long_name(user_long_name, context):
    if not user_long_name or len(user_long_name) > 30:
        raise ValidationError(
            _("Expected a user long name between 1 and 30 caracters. Got `{}`.").format(
                user_long_name
            )
        )


def _format_user_long_name(user_long_name):
    user_long_name_sanitized = _remove_accents_and_special_caracters(user_long_name)
    return _justify_left_with_blanks(user_long_name_sanitized.upper(), 30)


def _format_destinator_name(destinator_name):
    destinator_name_sanitized = _remove_accents_and_special_caracters(destinator_name)
    return _justify_left_with_blanks(destinator_name_sanitized[:30].upper(), 30)


def _format_transaction_reference(reference):
    if len(reference) > 19:
        reference = reference[-19:]
    reference_sanitized = _remove_accents_and_special_caracters(reference)
    return _justify_left_with_blanks(reference_sanitized.upper(), 19)


def _verify_transaction_type(transaction_type, context):
    if not transaction_type.isdigit():
        raise ValidationError(
            _("The transaction type must have 3 digits. Got `{}`.").format(
                transaction_type
            )
        )
    if len(transaction_type) != 3:
        raise ValidationError(
            _("Expected a transaction type with 3 caracters. Got `{}`.").format(
                transaction_type
            )
        )


def _verify_payment_amount(amount, context):
    if amount >= 10000000:
        raise ValidationError(
            _("EFT transfers support only payments below ten millions.").format(
                transaction_type
            )
        )


def _format_payment_amount(amount):
    return "{0:0>9.0f}".format(float_round(amount * 100, 0))


def _get_account_holder_name(account):
    name = account.acc_holder_name or ""
    return name.strip()


def _get_commercial_partner_name(payment):
    return payment.partner_id.commercial_partner_id.name


def _format_credit_detail_segment(payment):
    """Format the details for a single payment.

    :param payment: a recordset of either 0 or 1 account.payment.

        If the given recordset is empty, the returned segment will be filled with spaces.
    """
    if not payment:
        return " " * 240

    origin_account = payment.journal_id.bank_account_id
    destination_account = payment.partner_bank_id
    context = payment._context

    if not origin_account:
        raise ValidationError(
            _("The bank account is missing on the journal {}.").format(
                payment.journal_id.display_name
            )
        )

    if not destination_account:
        raise ValidationError(
            _("The destination bank account is missing on the payment {}.").format(
                payment.display_name
            )
        )

    destinator_name = _get_account_holder_name(
        destination_account
    ) or _get_commercial_partner_name(payment)

    transaction_type = payment.eft_transaction_type or DEFAULT_TRANSACTION_TYPE

    user_long_name = (
        payment.journal_id.eft_user_long_name or payment.journal_id.company_id.name
    )

    _verify_transaction_type(transaction_type, context)
    _verify_user_number(payment.journal_id.eft_user_number, context)
    _verify_user_short_name(payment.journal_id.eft_user_short_name, context)
    _verify_user_long_name(user_long_name, context)
    _verify_payment_amount(payment.amount, context)
    _verify_institution_number(destination_account.bank_id.canada_institution, context)
    _verify_institution_number(origin_account.bank_id.canada_institution, context)
    _verify_transit(destination_account.canada_transit, context)
    _verify_transit(origin_account.canada_transit, context)
    _verify_account_number(destination_account.acc_number, context)
    _verify_account_number(origin_account.acc_number, context)

    return (
        "{transaction_type}"
        "0{amount}"
        "{payment_date}"
        "0{destination_institution}{destination_transit}{destination_account}"
        "{zero_25}"
        "{user_short_name}"
        "{destinator_name}"
        "{user_long_name}"
        "{user_number}"
        "{transaction_reference}"
        "0{origin_institution}{origin_transit}{origin_account}"
        "{blank_39}"
        "{zero_11}".format(
            transaction_type=transaction_type,
            amount=_format_payment_amount(payment.amount),
            payment_date=_format_julian_date(payment.date),
            zero_25="0" * 25,
            destination_institution=destination_account.bank_id.canada_institution,
            destination_transit=destination_account.canada_transit,
            destination_account=_format_account_number(destination_account.acc_number),
            user_short_name=_format_user_short_name(
                payment.journal_id.eft_user_short_name
            ),
            destinator_name=_format_destinator_name(destinator_name),
            user_long_name=_format_user_long_name(user_long_name),
            user_number=payment.journal_id.eft_user_number,
            transaction_reference=_format_transaction_reference(payment.name),
            origin_institution=origin_account.bank_id.canada_institution,
            origin_transit=origin_account.canada_transit,
            origin_account=_format_account_number(origin_account.acc_number),
            blank_39=" " * 39,
            zero_11="0" * 11,
        )
    )


def format_credit_details_group(
    journal,
    payments,
    file_number,
    sequence_number,
):
    """Format a credit details section containing between 1 and 6 payments.

    :param journal: the bank journal of the EFT
    :param payments: a recordset of 1 to 6 account.payment.
    :param file_number: the sequence number of the EFT file
    :param sequence_number: the sequence number to use.
    """
    context = journal._context

    _verify_user_number(journal.eft_user_number, context)
    _verify_file_number(file_number, context)

    return (
        "C{sequence_number}{user_number}{file_number}"
        "{segment_1}"
        "{segment_2}"
        "{segment_3}"
        "{segment_4}"
        "{segment_5}"
        "{segment_6}".format(
            sequence_number=_format_sequence_number(sequence_number),
            user_number=journal.eft_user_number,
            file_number=_format_file_number(file_number),
            segment_1=_format_credit_detail_segment(payments[0:1]),
            segment_2=_format_credit_detail_segment(payments[1:2]),
            segment_3=_format_credit_detail_segment(payments[2:3]),
            segment_4=_format_credit_detail_segment(payments[3:4]),
            segment_5=_format_credit_detail_segment(payments[4:5]),
            segment_6=_format_credit_detail_segment(payments[5:6]),
        )
    )


def _format_total_amount(amount):
    return "{0:0>13.0f}".format(float_round(amount * 100, 0))


def _format_number_of_payments(number_of_payments):
    return "{0:0>7.0f}".format(number_of_payments)


def format_trailer(
    journal,
    file_number,
    sequence_number,
    total_amount,
    number_of_payments,
):
    """Generate the last line of the EFT file.

    :param journal: the bank journal
    :param file_number: the sequence number of the eft file.
    :param sequence_number: the sequence number of the trailer line.
    :param number_of_payments: the count of payments in the EFT.
    """
    context = journal._context

    _verify_user_number(journal.eft_user_number, context)
    _verify_file_number(file_number, context)

    return (
        "Z{sequence_number}{user_number}{file_number}"
        "{zero_22}"
        "0{total_amount}"
        "0{number_of_payments}"
        "{zero_44}"
        "{blank_1352}".format(
            sequence_number=_format_sequence_number(sequence_number),
            user_number=journal.eft_user_number,
            file_number=_format_file_number(file_number),
            zero_22="0" * 22,
            total_amount=_format_total_amount(total_amount),
            number_of_payments=_format_number_of_payments(number_of_payments),
            zero_44="0" * 44,
            blank_1352=" " * 1352,
        )
    )


def generate_eft(journal, payments, file_number):
    """Generate the complete EFT file.

    :param journal: the bank journal
    :param payments: the payments to include in the EFT
    :param file_number: the sequence number of the eft file
    """
    header = format_header(journal, file_number)

    next_sequence_number = 2

    # Generate one credit group for each multiple of 6 payments
    all_credit_group_details = []
    number_of_groups = math.ceil(len(payments) / 6)
    for i in range(number_of_groups):
        next_6_payments = payments[i * 6 : (i + 1) * 6]
        credit_group_details = format_credit_details_group(
            journal, next_6_payments, file_number, next_sequence_number
        )
        all_credit_group_details.append(credit_group_details)
        next_sequence_number += 1

    total_amount = sum(p.amount for p in payments)
    number_of_payments = len(payments)
    trailer = format_trailer(
        journal, file_number, next_sequence_number, total_amount, number_of_payments
    )

    return "{header}\n{credit_details}\n{trailer}".format(
        header=header,
        credit_details="\n".join(all_credit_group_details),
        trailer=trailer,
    )
