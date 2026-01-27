# Copyright 2026 Numigi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _


class AgedPartnerBalanceXslx(models.AbstractModel):
    """ Inherit XLSX report to add autofilters and customize columns. """
    _inherit = 'report.a_f_r.report_aged_partner_balance_xlsx'

    def _get_report_filters(self, report):
        """ Override to fix date formatting in the header. """
        filters = super(AgedPartnerBalanceXslx, self)._get_report_filters(report)
        # Convert date objects to string to avoid Excel serial number display (e.g., 46049)
        formatted_filters = []
        for key, value in filters:
            if key == _('Date at filter') and value:
                # Force conversion to string to ensure it displays as YYYY-MM-DD
                value = str(value)
            formatted_filters.append([key, value])
        return formatted_filters

    def _get_report_columns(self, report):
        """ Override columns to rename, reorder and hide based on options. """
        columns = super(AgedPartnerBalanceXslx, self)._get_report_columns(report)

        # Apply changes only if 'Invoice Date' method is selected
        if getattr(report, 'ageing_method', 'date_due') == 'date':

            # --- 1. Rename Buckets ---
            # Keys for summary view: 3=30d, 4=60d, 5=90d, 6=120d
            if 3 in columns: columns[3]['header'] = '1 - 30 j'
            if 4 in columns: columns[4]['header'] = '31 - 60 j'
            if 5 in columns: columns[5]['header'] = '61 - 90 j'
            if 6 in columns: columns[6]['header'] = '91 - 120 j'
            if 7 in columns: columns[7]['header'] = _('Older')

            # --- 2. Rename Residual to Total ---
            # Key 1 is Residual in summary view
            if 1 in columns:
                columns[1]['header'] = _('Total')

            # --- 3. Hide Current column if Total is 0 ---
            # Key 2 is Current in summary view
            if 2 in columns:
                # Calculate total of 'cumul_current' across all accounts
                total_current = sum(account.cumul_current for account in report.account_ids)
                if total_current == 0:
                    del columns[2]

            # --- 4. Reorder Columns (Move Total to the end) ---
            # Standard Order (keys): 0 (Partner), 1 (Residual), 2 (Current), 3, 4, 5, 6, 7 (Older)
            # Desired Order: Partner, [Current], Buckets..., Older, Total

            new_columns = {}
            new_index = 0

            # Helper to add column if it exists
            def add_col(old_index):
                nonlocal new_index
                if old_index in columns:
                    new_columns[new_index] = columns[old_index]
                    new_index += 1

            add_col(0)  # Partner
            add_col(2)  # Current (if not deleted)
            add_col(3)  # 1-30
            add_col(4)  # 31-60
            add_col(5)  # 61-90
            add_col(6)  # 91-120
            add_col(7)  # Older
            add_col(1)  # Total (was Residual)

            return new_columns

        return columns

    def _generate_report_content(self, workbook, report):
        """ Override to apply autofilter on the header row. """
        # Execute the original method to write data
        super(AgedPartnerBalanceXslx, self)._generate_report_content(workbook, report)

        # Apply Excel Autofilter
        if self.sheet:
            # Determine the last column index dynamically
            last_col_idx = max(self.columns.keys()) if self.columns else 10

            # Apply filter on the header row (typically row 4, index 4 is line 5)
            # Adjust row index if your header position changes
            header_row_idx = 4
            self.sheet.autofilter(header_row_idx, 0, self.row_pos, last_col_idx)