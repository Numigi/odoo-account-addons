# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import csv
import traceback
from decimal import Decimal
from datetime import datetime

ZERO = Decimal("0")


class BankStatementLoader:
    def __init__(self, config):
        self._config = config

        self._first_row = config.get("first_row", 0)
        self._delimiter = config.get("delimiter", ",")
        self._quotechar = config.get("quotechar")

        self._date_index = self._get_index_of("date")
        self._date_format = self._get_format_of("date")

        self._amount_index = self._get_index_of("amount")
        self._withdraw_index = self._get_index_of("withdraw")
        self._deposit_index = self._get_index_of("deposit")
        self._balance_index = self._get_index_of("balance")
        self._description_index = self._get_index_of("description")
        self._reference_index = self._get_index_of("reference")
        self._currency_index = self._get_index_of("currency")
        self._currency_amount_index = self._get_index_of("currency_amount")

    def _get_index_of(self, field_name):
        field = self._config.get(field_name)
        return field["index"] if field else None

    def _get_format_of(self, field_name):
        field = self._config.get(field_name)
        return field["format"] if field else None

    def load(self, file):
        rows = self._iter_rows(file)
        return {"rows": [self._parse_row(r) for r in rows]}

    def parse_decimal(self, amount_str):
        return 

    def _parse_row(self, row):
        try:
            return {
                "date": self._get_date(row),
                "amount": _decimal_to_string(self._get_amount(row)),
                "currency": self._get_currency(row),
                "currency_amount": _decimal_to_string(self._get_currency_amount(row)),
                "balance": _decimal_to_string(self._get_balance(row)),
                "description": self._get_description(row),
                "reference": self._get_reference(row),
            }
        except Exception as err:
            return {
                "traceback": traceback.format_exc(),
                "error": str(err),
            }

    def _get_date(self, row):
        if self._date_index is not None:
            str_date = self._get_cell(row, self._date_index)
            date_ = datetime.strptime(str_date, self._date_format).date()
            return str(date_)

    def _get_description(self, row):
        if self._description_index is not None:
            return self._get_cell(row, self._description_index)

    def _get_reference(self, row):
        if self._reference_index is not None:
            return self._get_cell(row, self._reference_index)

    def _get_currency(self, row):
        if self._currency_index is not None:
            return self._get_cell(row, self._currency_index)

    def _get_amount(self, row):
        amount = self._get_single_column_amount(row) or ZERO
        withdraw = self._get_withdraw(row) or ZERO
        deposit = self._get_deposit(row) or ZERO
        return amount + deposit - withdraw

    def _get_single_column_amount(self, row):
        if self._amount_index is not None:
            return self._get_cell_decimal(row, self._amount_index)

    def _get_withdraw(self, row):
        if self._withdraw_index is not None:
            return self._get_cell_decimal(row, self._withdraw_index)

    def _get_deposit(self, row):
        if self._deposit_index is not None:
            return self._get_cell_decimal(row, self._deposit_index)

    def _get_currency_amount(self, row):
        if self._currency_amount_index is not None:
            amount = self._get_amount(row)
            currency_amount = self._get_cell_decimal(row, self._currency_amount_index)

            if amount and currency_amount and _not_same_sign(amount, currency_amount):
                currency_amount *= -1

            return currency_amount

    def _get_balance(self, row):
        if self._balance_index is not None:
            return self._get_cell_decimal(row, self._balance_index)

    def _get_cell_decimal(self, row, index):
        amount_str = self._get_cell(row, index)
        return Decimal(amount_str) if amount_str else None

    def _get_cell(self, row, index):
        if index < len(row):
            return row[index].strip()
        else:
            return ""

    def _iter_rows(self, file):
        reader = csv.reader(file, delimiter=self._delimiter, quotechar=self._quotechar)

        for i in range(self._first_row):
            next(reader, None)

        for row in reader:
            yield row


def _not_same_sign(a1, a2):
    return (a1 < 0 and a2 > 0) or (a1 > 0 and a2 < 0)


def _decimal_to_string(amount):
    if amount is not None:
        return amount.to_eng_string()
