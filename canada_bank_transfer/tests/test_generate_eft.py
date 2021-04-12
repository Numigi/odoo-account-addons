# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime
from ddt import ddt, data
from freezegun import freeze_time
from odoo.exceptions import ValidationError
from ..generate_eft import (
    _format_payment_amount,
    _format_total_amount,
    format_header,
    format_credit_details_group,
    format_trailer,
    generate_eft,
)
from .common import (
    USER_NUMBER,
    DESTINATION,
    EFTCase,
)


@pytest.mark.parametrize('number,expected_value', [
    (10, '000001000'),
    (10.23, '000001023'),
    (10.234, '000001023'),
    (10.235, '000001024'),
    (1.49999999, '000000150')
])
def test_format_payment_amount(number, expected_value):
    assert _format_payment_amount(number) == expected_value


@pytest.mark.parametrize('number,expected_value', [
    (10, '0000000001000'),
    (10.23, '0000000001023'),
    (10.234, '0000000001023'),
    (10.235, '0000000001024'),
    (1.49999999, '0000000000150')
])
def test_format_total_amount(number, expected_value):
    assert _format_total_amount(number) == expected_value


@ddt
class TestFormatEFTHeader(EFTCase):

    def test_record_type_is_a(self):
        header = format_header(self.journal, 1)
        assert header[0] == 'A'

    def test_sequence_is_always_one(self):
        header = format_header(self.journal, 999)
        assert header[1:10] == '000000001'

    def test_user_number(self):
        header = format_header(self.journal, 1)
        assert header[10:20] == USER_NUMBER

    @data(False, '123456789')
    def test_invalid_user_number_raises_error(self, wrong_number):
        self.journal.eft_user_number = wrong_number
        with pytest.raises(ValidationError):
            format_header(self.journal, 1)

    @data(
        (1, '0001'),
        (999, '0999'),
        (9999, '9999'),
    )
    def test_file_number(self, data_):
        number, formatted_number = data_
        header = format_header(self.journal, number)
        assert header[20:24] == formatted_number

    def test_file_number_above_9999_raises_error(self):
        with pytest.raises(ValidationError):
            format_header(self.journal, 10000)

    @data(
        ('2019-06-30', '019181'),
        ('2020-01-01', '020001'),
    )
    def test_format_header_create_date(self, data_):
        date, formatted_date = data_
        with freeze_time(date):
            header = format_header(self.journal, 1)
            assert header[24:30] == formatted_date

    def test_destination_data_center_code(self):
        header = format_header(self.journal, 1)
        assert header[30:35] == DESTINATION

    @data(False, '1234', 'abcde')
    def test_invalid_destination_data_center_code_raises_error(self, wrong_code):
        self.journal.eft_destination = wrong_code
        with pytest.raises(ValidationError):
            format_header(self.journal, 1)

    def test_blank_from_35_to_55(self):
        header = format_header(self.journal, 1)
        assert header[35:55] == " " * 20

    def test_currency_code(self):
        header = format_header(self.journal, 1)
        assert header[55:58] == "CAD"

    def test_if_no_journal_currency_then_company_currency_is_used(self):
        journal = self.journal.copy({'currency_id': False})
        header = format_header(journal, 1)
        assert header[55:58] == journal.company_id.currency_id.name

    def test_currency_code_with_usd(self):
        self.journal.currency_id = self.env.ref('base.USD')
        header = format_header(self.journal, 1)
        assert header[55:58] == "USD"

    def test_blank_from_58_to_1464(self):
        header = format_header(self.journal, 1)
        assert header[58:1464] == " " * 1406


@ddt
class TestEFTCreditDetails(EFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pmt_1 = cls.generate_payment(cls.td_account, 111.11)
        cls.pmt_2 = cls.generate_payment(cls.rbc_account, 222.22)
        cls.payments = cls.pmt_1 | cls.pmt_2

    def test_record_length(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert len(record) == 1464

    def test_record_type_is_c(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[0] == 'C'

    @data(
        (2, '000000002'),
        (999, '000000999'),
    )
    def test_sequence_number(self, data_):
        number, formatted_number = data_
        record = format_credit_details_group(self.journal, self.payments, 1, number)
        assert record[1:10] == formatted_number

    def test_user_number(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[10:20] == USER_NUMBER

    def test_file_number(self):
        record = format_credit_details_group(self.journal, self.payments, 999, 2)
        assert record[20:24] == '0999'

    def test_operation_code(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[24:27] == '450'

    def test_operation_code_is_450_by_default(self):
        self.payments[0].write({'eft_transaction_type': None})
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[24:27] == '450'

    def test_payment_amount(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[27:37] == '0000011111'  # payment 1: 111.11
        assert record[27 + 240:37 + 240] == '0000022222'  # payment 2: 222.22

    def test_format_header_create_date(self):
        with freeze_time('2019-06-30'):
            self.payments[0].move_id.date = datetime.now().date()
            record = format_credit_details_group(self.journal, self.payments, 1, 2)
            assert record[37:43] == '019181'

    def test_destination_institution(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[43:47] == '0004'  # '0{institution}'

    def test_destination_transit(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[47:52] == '20002'

    @data(
        ('1234567', '1234567     '),
        ('12345678', '12345678    '),
        ('123456789012', '123456789012'),
    )
    def test_destination_account(self, data_):
        self.td_account.acc_number = data_[0]
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[52:64] == data_[1]

    @data(
        '1234567 ',  # non-digit
        '123456',  # too short
        '1234567890123'  # too long
    )
    def test_if_account_number_too_short_raise_error(self, wrong_number):
        self.td_account.acc_number = wrong_number
        with pytest.raises(ValidationError):
            format_credit_details_group(self.journal, self.payments, 1, 2)

    def test_zeros_from_64_to_89(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[64:89] == '0' * 25

    def test_user_short_name(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[89:104] == 'YOUR COMPANY   '  # 15 caracters

    def test_accents_are_removed_from_user_short_name(self):
        self.journal.eft_user_short_name = 'Québec Inc. *'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[89:104] == 'QUEBEC INC. _  '  # 15 caracters

    def test_destinator_short_name(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[104:134] == 'SUPPLIER 1                    '  # 30 caracters

    def test_destinator_short_name__uses_acc_holder_name_if_available(self):
        self.payments[0].partner_bank_id.acc_holder_name = "Custom Account Holder Name"
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[104:134] == 'CUSTOM ACCOUNT HOLDER NAME    '  # 30 caracters

    def test_accents_are_removed_from_destinator_name(self):
        self.td_account.partner_id.name = '12345 Québec Inc. *test*'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[104:134] == '12345 QUEBEC INC. _TEST_      '  # 30 caracters

    def test_user_long_name(self):
        self.journal.company_id.name = 'Your Company Inc.'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[134:164] == 'YOUR COMPANY INC.             '  # 30 caracters

    def test_specific_user_long_name(self):
        self.journal.eft_user_long_name = 'Specific User Long Name'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[134:164] == 'SPECIFIC USER LONG NAME       '

    def test_accents_are_removed_from_user_long_name(self):
        self.journal.company_id.name = 'Your Company Inc. *test*'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[134:164] == 'YOUR COMPANY INC. _TEST_      '  # 30 caracters

    def test_user_number_at_164(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[164:174] == USER_NUMBER

    def test_transaction_reference_number(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        reference = record[174:192]
        assert reference.strip() == self.pmt_1.name.replace('/', '_')

        reference_2 = record[174 + 240:192 + 240]
        assert reference_2.strip() == self.pmt_2.name.replace('/', '_')

    def test_transaction_reference_number_with_long_payment_name(self):
        self.pmt_1.name = 'SUPP.OUT/2019/1234567'
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        reference = record[174:193]
        assert reference == 'PP.OUT_2019_1234567'

    def test_origin_institution(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[193:197] == "0006"

    def test_origin_transit(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[197:202] == "10001"

    def test_origin_account_number(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[202:214] == "1000001     "

    def test_user_information(self):
        """Test the optional user information field.

        This field is optional. For now, it is not implemented in the module.
        """
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[214:229] == " " * 15

    def test_blank_from_229_to_253(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[229:253] == " " * 24

    def test_zero_from_253_to_264(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert record[253:264] == "0" * 11


@ddt
class TestEFTCreditDetailsWith6Payments(EFTCase):
    """Test a credit details group with 6 payments.

    6 is the maximum of payments inside a credit details group.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pmt_1 = cls.generate_payment(cls.td_account, 111.11)
        cls.pmt_2 = cls.generate_payment(cls.rbc_account, 222.22)
        cls.pmt_3 = cls.generate_payment(cls.rbc_account, 333.33)
        cls.pmt_4 = cls.generate_payment(cls.rbc_account, 444.44)
        cls.pmt_5 = cls.generate_payment(cls.rbc_account, 555.55)
        cls.pmt_6 = cls.generate_payment(cls.rbc_account, 666.66)
        cls.payments = cls.pmt_1 | cls.pmt_2 | cls.pmt_3 | cls.pmt_4 | cls.pmt_5 | cls.pmt_6

    def test_record_length(self):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        assert len(record) == 1464

    @data(
        (0, '0000011111'),
        (1, '0000022222'),
        (2, '0000033333'),
        (3, '0000044444'),
        (4, '0000055555'),
        (5, '0000066666'),
    )
    def test_payment_amount(self, data_):
        record = format_credit_details_group(self.journal, self.payments, 1, 2)
        offset = 240 * data_[0]
        assert record[27 + offset:37 + offset] == data_[1]


@ddt
class TestEFTTrailer(EFTCase):

    def test_trailer_length(self):
        trailer = format_trailer(self.journal, 1, 1, 1, 1)
        assert len(trailer) == 1464

    def test_record_type_is_z(self):
        trailer = format_trailer(self.journal, 1, 1, 1, 1)
        assert trailer[0] == 'Z'

    def test_sequence_number(self):
        trailer = format_trailer(self.journal, 1, 123, 1, 1)
        assert trailer[1:10] == '000000123'

    def test_user_number(self):
        trailer = format_trailer(self.journal, 1, 1, 1, 1)
        assert trailer[10:20] == USER_NUMBER

    def test_zero_from_24_to_46(self):
        trailer = format_trailer(self.journal, 999, 1, 1, 1)
        assert trailer[24:46] == "0" * 22

    def test_total_amount(self):
        trailer = format_trailer(self.journal, 999, 1, 123.45, 1)
        assert trailer[46:60] == "00000000012345"

    def test_number_of_payments(self):
        trailer = format_trailer(self.journal, 999, 1, 1, 123)
        assert trailer[60:68] == "00000123"

    def test_zero_from_68_to_112(self):
        trailer = format_trailer(self.journal, 999, 1, 1, 1)
        assert trailer[68:112] == "0" * 44

    def test_blank_from_112_to_1464(self):
        trailer = format_trailer(self.journal, 999, 1, 1, 1)
        assert trailer[112:1464] == " " * 1352


class CompleteEFTCase(EFTCase):

    @classmethod
    def _generate_payments(cls, number_of_payments):
        payments = cls.env['account.payment']
        for i in range(number_of_payments):
            payments |= cls.generate_payment(cls.rbc_account, i + 1)
        return payments


@ddt
class TestCompleteEFTLength(CompleteEFTCase):

    @data(1, 5, 6)
    def test_eft_length_with_6_payments_or_less(self, number_of_payments):
        payments = self._generate_payments(number_of_payments)
        eft = generate_eft(self.journal, payments, 1)
        assert len(eft) == 4394  # 1464 + 1464 + 1464 (header + details + trailer) + 2 \n

    @data(7, 12)
    def test_eft_length_with_7_to_12_payments(self, number_of_payments):
        payments = self._generate_payments(number_of_payments)
        eft = generate_eft(self.journal, payments, 1)
        assert len(eft) == 5859  # 1464 + 1464 * 2 + 1464 (header + details + trailer) + 3 \n

    @data(13, 18)
    def test_eft_length_with_13_to_18_payments(self, number_of_payments):
        payments = self._generate_payments(number_of_payments)
        eft = generate_eft(self.journal, payments, 1)
        assert len(eft) == 7324  # 1464 + 1464 * 3 + 1464 (header + details + trailer) + 4 \n


@ddt
class TestCompleteEFTAmountPosition(CompleteEFTCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payments = cls._generate_payments(20)

    @data(
        # (formatted_payment_amount, amount_index_in_file)
        ('0000000100', 1492),  # 1492 = 1464 + 1 + 27 (header + \n + 27)
        ('0000000200', 1732),  # 1732 = 1492 + 240
        ('0000000500', 2452),  # 2452 = 1492 + 240 * 4
        ('0000000600', 2692),  # 2692 = 1492 + 240 * 5
        ('0000000700', 2957),  # 2957 = 1464 + 1 + 1464 + 1 + 27 (header + \n + group1 + \n + 27)
        ('0000001200', 4157),  # 4157 = 2957 + 240 * 5
        ('0000001300', 4422),  # 4421 = 1464 * 3 + 3 + 27
        ('0000001800', 5622),  # 5622 = 4421 + 240 * 5
        ('0000001900', 5887),  # 5887 = 1464 * 4 + 4 + 27
        ('0000002000', 6127),  # 6127 = 5887 + 240
    )
    def test_payments_order(self, data_):
        formatted_payment_amount, amount_index_in_file = data_
        eft = generate_eft(self.journal, self.payments, 1)
        assert eft[amount_index_in_file:amount_index_in_file + 10] == formatted_payment_amount
