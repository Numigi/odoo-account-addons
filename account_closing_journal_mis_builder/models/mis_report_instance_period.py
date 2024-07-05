# Copyright 2020 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.osv.expression import AND


class MisReportInstancePeriod(models.Model):

    _inherit = "mis.report.instance.period"

    def _get_additional_move_line_filter(self):
        domain = super()._get_additional_move_line_filter()

        if self.report_id.exclude_closing_entries:
            domain = AND([domain, [("is_closing", "=", False)]])

        return domain
