# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    analytic_account_iteration = fields.Boolean(
        "Iterate on Analytic Accounts"
    )
    analytic_group_account_iteration = fields.Boolean(
        "Iterate on Analytic Account Groups"
    )

    def export_xls(self):
        self.ensure_one()
        if self._context.get('automated_edition'):
            super(MisReportInstance, self).with_delay().export_xls()
        return super(MisReportInstance, self).export_xls()
