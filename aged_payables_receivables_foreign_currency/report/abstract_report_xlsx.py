# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account_financial_report.report.abstract_report_xlsx import (
    AbstractReportXslx as AbstractReportXslxOriginal,
)


class AbstractReportXslx(AbstractReportXslxOriginal):
    def write_line_from_dict(self, line_dict, report_data):
        """Write a line on current line"""
        for col_pos, column in report_data["columns"].items():
            value = line_dict.get(column["field"], False)
            cell_type = column.get("type", "string")

            # If the column is a currency column, we need to get the currency name
            if column["field"] == "currency_id":
                if isinstance(value, tuple):
                    value = value[0]
                currency = self.env["res.currency"].browse(value).name
                line_dict["currency_id"] = value = currency

            if cell_type == "string":
                if line_dict.get("type", "") == "group_type":
                    report_data["sheet"].write_string(
                        report_data["row_pos"],
                        col_pos,
                        value or "",
                        report_data["formats"]["format_bold"],
                    )
                else:
                    if (
                        not isinstance(value, str)
                        and not isinstance(value, bool)
                        and not isinstance(value, int)
                    ):
                        value = value and value.strftime("%d/%m/%Y")
                    report_data["sheet"].write_string(
                        report_data["row_pos"], col_pos, value or ""
                    )
            elif cell_type == "amount":
                if (
                    line_dict.get("account_group_id", False)
                    and line_dict["account_group_id"]
                ):
                    cell_format = report_data["formats"]["format_amount_bold"]
                else:
                    cell_format = report_data["formats"]["format_amount"]
                report_data["sheet"].write_number(
                    report_data["row_pos"], col_pos, float(value), cell_format
                )
            elif cell_type == "amount_currency":
                if line_dict.get("currency_name", False):
                    format_amt = self._get_currency_amt_format_dict(
                        line_dict, report_data
                    )
                    report_data["sheet"].write_number(
                        report_data["row_pos"], col_pos, float(value), format_amt
                    )
            elif cell_type == "currency_name":
                report_data["sheet"].write_string(
                    report_data["row_pos"],
                    col_pos,
                    value or "",
                    report_data["formats"]["format_right"],
                )
            else:
                self.write_non_standard_column(cell_type, col_pos, value)
        report_data["row_pos"] += 1

    AbstractReportXslxOriginal.write_line_from_dict = write_line_from_dict
