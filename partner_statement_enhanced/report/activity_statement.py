# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from collections import defaultdict


class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _inherit = 'report.partner_statement.activity_statement'

    def _get_account_initial_balance(self, company_id, partner_ids,
                                     date_start, account_type):
        balance_start = defaultdict(list)
        partners = tuple(partner_ids)
        # pylint: disable=E8103
        sql_query = """
               WITH Q1 AS (%s), Q2 AS (%s)
               SELECT partner_id, currency_id, SUM(balance) AS balance
               FROM Q2
               GROUP BY partner_id, currency_id
           """ % (self._initial_balance_sql_q1(partners, date_start, account_type),
                  self._initial_balance_sql_q2(company_id))

        self.env.cr.execute(sql_query)
        res = self.env.cr.dictfetchall()
        # Grouping and formatting result
        for item in res:
            balance_start[item['partner_id']].append(
                {'currency_id': item['currency_id'], 'balance': item['balance']})
        return balance_start
