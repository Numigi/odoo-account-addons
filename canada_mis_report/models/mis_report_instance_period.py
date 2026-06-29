# © 2026 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    def _get_additional_query_filter(self, query):
        # 1. Fetch default domains (e.g., multi-company filters)
        domain = super()._get_additional_query_filter(query)

        analytic_domain = self.env.context.get("mis_analytic_domain", [])

        target_model = query.model_id.model

        # 3. Verify if the target model has the 'journal_id' field to prevent crashes
        if "journal_id" in self.env[target_model]._fields:
            # 4. Iterate over the analytic domain to extract only the journal_id condition
            for condition in analytic_domain:
                if isinstance(condition, (list, tuple)) and len(condition) == 3:
                    if condition[0] == "journal_id":
                        # We append the exact condition directly to our query's domain
                        domain.append(condition)

        return domain
