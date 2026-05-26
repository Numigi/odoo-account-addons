# © 2026 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _

import logging
_logger = logging.getLogger(__name__)

class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def _inverse_comparison_mode(self):
        super()._inverse_comparison_mode()
        for record in self:
            # Check if comparison mode is disabled and periods exist
            if not record.comparison_mode and record.period_ids:
                # Override the hardcoded "Default" name
                # Use standard Odoo translation function _()
                record.period_ids.write({'name': _('Current Period')})

