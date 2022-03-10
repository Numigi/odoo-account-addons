# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    project_id = fields.Many2one("project.project")

    @api.onchange("project_id")
    def _onchange_project(self):
        if self.project_id:
            self.account_analytic_id = self.project_id.analytic_account_id
