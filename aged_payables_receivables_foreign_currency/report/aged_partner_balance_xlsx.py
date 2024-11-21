# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class AgedPartnerBalanceXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_aged_partner_balance_xlsx"

    def _get_col_pos_footer_label(self, report):
        return 2 if not report.show_move_line_details else 8

    def _get_col_pos_final_balance_label(self):
        return 8

    def _get_report_columns(self, report):
        def insert_and_update_indexes(original_dict, new_entries, insert_position):
            # Create a new dictionary to hold the updated entries
            updated_dict = {}

            # Insert the new entries at the specified position
            for i in range(insert_position):
                updated_dict[i] = original_dict[i]

            for i, entry in enumerate(new_entries, start=insert_position):
                updated_dict[i] = entry

            for i in range(insert_position, len(original_dict)):
                updated_dict[i + len(new_entries)] = original_dict[i]

            return updated_dict

        if not report.show_move_line_details:
            res = super()._get_report_columns(report)
            # New entries to insert
            new_entries = [
                {"header": _("Currency"), "field": "currency_id", "width": 14},
                {
                    "header": _("Amount Currency"),
                    "field": "amount_currency",
                    "type": "amount",
                    "width": 17,
                },
            ]

            # Insert new entries at position 1
            insert_position = 1
            updated_dict = insert_and_update_indexes(res, new_entries, insert_position)
            return updated_dict
        else:

            res = super()._get_report_columns(report)

            # New entries to insert
            new_entries = [
                {"header": _("Currency"), "field": "currency_id", "width": 14},
                {
                    "header": _("Amount Currency"),
                    "field": "amount_currency",
                    "type": "amount",
                    "width": 17,
                },
            ]
            # Insert new entries before the "Residual" entry (index 7)
            insert_position = 7
            updated_dict = insert_and_update_indexes(res, new_entries, insert_position)
            return updated_dict
        return
