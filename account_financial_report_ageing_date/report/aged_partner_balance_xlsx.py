# Copyright 2026 Numigi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AgedPartnerBalanceXslx(models.AbstractModel):
    """ Inherit XLSX report to add autofilters. """
    _inherit = 'report.a_f_r.report_aged_partner_balance_xlsx'

    def _generate_report_content(self, workbook, report):
        """ Override to apply autofilter on the header row. """
        # Execute the original method to write data
        super(AgedPartnerBalanceXslx, self)._generate_report_content(workbook, report)

        # Apply Excel Autofilter
        # Note: self.row_pos is incremented by the original method.
        # We assume the data starts around row 5 (title + headers).
        # Depending on the complexity of the report, we apply filter to the widest possible range.
        if self.sheet:
            # max(self.columns.keys()) gives the index of the last column
            last_col_idx = max(self.columns.keys()) if self.columns else 10

            # Apply filter from row 4 (headers usually) to the current row
            # Adjust '4' if the header row index changes in future versions
            header_row_idx = 4
            self.sheet.autofilter(header_row_idx, 0, self.row_pos, last_col_idx)