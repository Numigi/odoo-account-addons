# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import csv
from babel.numbers import (
    parse_decimal,
    NumberFormatError,
    validate_currency,
    UnknownCurrencyError,
)
from decimal import Decimal
from datetime import datetime
from odoo import _
from .error import BankStatementError

ZERO = Decimal("0")
LOCALE_MAP = {
    (".", ""): "en_US",
    (".", " "): "en_US",
    (".", ","): "en_US",
    (",", "."): "de",
    (",", ""): "ru",
    (",", " "): "ru",
}
SEPARATOR = ["", " ", ","]


class BankStatementLoader:
    def __init__(self, config):
        self._config = config

        self._first_row_index = config.get("first_row_index", 0)
        self._delimiter = config.get("delimiter", ",")
        self._quotechar = config.get("quotechar")

        self._decimal_separator = config.get("decimal_separator")
        self._thousands_separator = config.get("thousands_separator")

        self._date_index = self._get_index_of("date")
        self._date_format = self._get_format_of("date")

        self._amount_index = self._get_index_of("amount")
        self._withdraw_index = self._get_index_of("withdraw")
        self._reverse_withdraw = self._is_reversed("withdraw")
        self._deposit_index = self._get_index_of("deposit")
        self._reverse_deposit = self._is_reversed("deposit")
        self._balance_index = self._get_index_of("balance")
        self._description_index = self._get_index_of("description")
        self._reference_index = self._get_index_of("reference")
        self._partner_name_index = self._get_index_of("partner_name")
        self._currency_index = self._get_index_of("currency")
        self._currency_amount_index = self._get_index_of("currency_amount")

    def _get_index_of(self, field_name):
        field = self._config.get(field_name)
        return field["index"] if field else None

    def _get_format_of(self, field_name):
        field = self._config.get(field_name)
        return field["format"] if field else None

    def _is_reversed(self, field_name):
        field = self._config.get(field_name)
        return field.get("reverse") if field else False

    def load(self, file):
        rows = self._iter_rows(file)
        return {"rows": [self.parse_row(r) for r in rows]}

    def parse_row(self, row):
        return {
            "date": self._get_date(row),
            "amount": self._get_amount(row),
            "currency": self._get_currency(row),
            "currency_amount": self._get_currency_amount(row),
            "balance": self._get_balance(row),
            "description": self._get_description(row),
            "reference": self._get_reference(row),
            "partner_name": self._get_partner_name(row),
        }

    def _get_date(self, row):
        if self._date_index is not None:
            str_date = self._get_cell(row, self._date_index)
            return parse_date_or_error(str_date, self._date_format)
        return None

    def _parse_date(self, str_date):
        return datetime.strptime(str_date, self._date_format).date()

    def _get_parse_date_error(self, str_date):
        return BankStatementError(
            msg=_("The given date ({date}) does not match the format {format}."),
            kwargs={"date": str_date, "format": self._date_format},
        )

    def _get_description(self, row):
        if self._description_index is not None:
            return self._get_cell(row, self._description_index)
        return None

    def _get_reference(self, row):
        if self._reference_index is not None:
            return self._get_cell(row, self._reference_index)
        return None

    def _get_partner_name(self, row):
        if self._partner_name_index is not None:
            return self._get_cell(row, self._partner_name_index)
        return None

    def _get_currency(self, row):
        if self._currency_index is not None:
            value = self._get_cell(row, self._currency_index)

            if not value and self._get_currency_amount(row):
                return BankStatementError(
                    msg=_(
                        "The currrency is required when an amount "
                        "in foreign currency is given."
                    ),
                )

            if value:
                return parse_currency_or_error(value)
        return None

    def _get_amount(self, row):
        amount = self._get_single_index_amount(row)
        withdraw = self._get_withdraw(row)
        deposit = self._get_deposit(row)

        error = next(
            (
                el
                for el in (amount, withdraw, deposit)
                if isinstance(el, BankStatementError)
            ),
            None,
        )

        if error:
            return error

        return (amount or ZERO) + (deposit or ZERO) - (withdraw or ZERO)

    def _get_single_index_amount(self, row):
        if self._amount_index is not None:
            return self._get_cell_decimal(row, self._amount_index)

    def _get_withdraw(self, row):
        if self._withdraw_index is not None:
            amount = self._get_cell_decimal(row, self._withdraw_index)
            if self._reverse_withdraw:
                amount = -amount if amount is not None else None
            return amount
        return None

    def _get_deposit(self, row):
        if self._deposit_index is not None:
            amount = self._get_cell_decimal(row, self._deposit_index)
            if self._reverse_deposit:
                amount = -amount if amount is not None else None
            return amount
        return None

    def _get_currency_amount(self, row):
        if self._currency_amount_index is not None:
            amount = self._get_amount(row)
            currency_amount = self._get_cell_decimal(row, self._currency_amount_index)

            if (
                isinstance(amount, Decimal)
                and isinstance(currency_amount, Decimal)
                and _not_same_sign(amount, currency_amount)
            ):
                currency_amount *= -1

            return currency_amount
        return None

    def _get_balance(self, row):
        if self._balance_index is not None:
            return self._get_cell_decimal(row, self._balance_index)
        return None

    def _get_cell_decimal(self, row, index):
        amount_str = self._get_cell(row, index)
        thousands_separator = "" if not self._thousands_separator else " "
        locale = LOCALE_MAP.get((self._decimal_separator, thousands_separator), "en_US")

        if self._decimal_separator == "." and self._thousands_separator in SEPARATOR:
            amount_str = amount_str.replace(" ", "")

        return parse_decimal_or_error(amount_str, locale)

    def _get_cell(self, row, index):
        if index < len(row):
            return row[index].strip()
        return ""

    def _iter_rows(self, file):
        reader = csv.reader(file, delimiter=self._delimiter, quotechar=self._quotechar)

        for __ in range(self._first_row_index):
            next(reader, None)

        for row in reader:
            if row:
                yield row


def _not_same_sign(a1, a2):
    return (a1 < 0 and a2 > 0) or (a1 > 0 and a2 < 0)


def parse_date_or_error(str_date, format_):
    try:
        date_ = _parse_date(str_date, format_)
        return date_.strftime("%Y-%m-%d")
    except ValueError:
        return _get_parse_date_error(str_date, format_)


def _parse_date(str_date, format_):
    return datetime.strptime(str_date, format_).date()


def _get_parse_date_error(str_date, format_):
    return BankStatementError(
        msg=_("The given date ({date}) does not match the format {format}."),
        kwargs={"date": str_date, "format": format_},
    )


def parse_decimal_or_error(value, locale="en_US"):
    try:
        return _parse_decimal(value, locale)
    except NumberFormatError:
        return _get_decimal_error(value)


def _parse_decimal(value, locale):
    return parse_decimal(value, locale) if value else None


def _get_decimal_error(value):
    return BankStatementError(
        msg=_("The given value ({}) does not seem to be a valid number."),
        args=(value,),
    )


def parse_currency_or_error(value):
    try:
        validate_currency(value)
        return value
    except UnknownCurrencyError:
        return _get_currency_error(value)


def _get_currency_error(value):
    return BankStatementError(
        msg=_("The given value ({}) does not seem to be a valid curency code."),
        args=(value,),
    )
