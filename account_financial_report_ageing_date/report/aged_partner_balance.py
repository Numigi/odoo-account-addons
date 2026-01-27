# Copyright 2026 Numigi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AgedPartnerBalanceReport(models.TransientModel):
    _inherit = 'report_aged_partner_balance'

    ageing_method = fields.Selection(
        selection=[
            ('date_due', 'Due Date'),
            ('date', 'Invoice Date'),
        ],
        readonly=True
    )

    def _inject_line_values(self, only_empty_partner_line=False):
        """ Inject report values for report_aged_partner_balance_line.

        Override to dynamically change the date field used for computation
        (rlo.date vs rlo.date_due) based on the user's choice.
        """
        # Determine which SQL field to use based on the user selection
        # 'rlo' is the alias for report_open_items_move_line
        date_field = 'rlo.date_due'
        if self.ageing_method == 'date':
            date_field = 'rlo.date'

        # We format the query string to inject the correct field name
        query_inject_line = """
WITH
    date_range AS
        (
            SELECT
                DATE %s AS date_current,
                DATE %s - INTEGER '30' AS date_less_30_days,
                DATE %s - INTEGER '60' AS date_less_60_days,
                DATE %s - INTEGER '90' AS date_less_90_days,
                DATE %s - INTEGER '120' AS date_less_120_days
        )
INSERT INTO
    report_aged_partner_balance_line
    (
        report_partner_id,
        create_uid,
        create_date,
        partner,
        amount_residual,
        current,
        age_30_days,
        age_60_days,
        age_90_days,
        age_120_days,
        older
    )
SELECT
    rp.id AS report_partner_id,
    %s AS create_uid,
    NOW() AS create_date,
    rp.name,
    SUM(rlo.amount_residual) AS amount_residual,
    SUM(
        CASE
            WHEN {date_field} >= date_range.date_current
            THEN rlo.amount_residual
        END
    ) AS current,
    SUM(
        CASE
            WHEN
                {date_field} >= date_range.date_less_30_days
                AND {date_field} < date_range.date_current
            THEN rlo.amount_residual
        END
    ) AS age_30_days,
    SUM(
        CASE
            WHEN
                {date_field} >= date_range.date_less_60_days
                AND {date_field} < date_range.date_less_30_days
            THEN rlo.amount_residual
        END
    ) AS age_60_days,
    SUM(
        CASE
            WHEN
                {date_field} >= date_range.date_less_90_days
                AND {date_field} < date_range.date_less_60_days
            THEN rlo.amount_residual
        END
    ) AS age_90_days,
    SUM(
        CASE
            WHEN
                {date_field} >= date_range.date_less_120_days
                AND {date_field} < date_range.date_less_90_days
            THEN rlo.amount_residual
        END
    ) AS age_120_days,
    SUM(
        CASE
            WHEN {date_field} < date_range.date_less_120_days
            THEN rlo.amount_residual
        END
    ) AS older
FROM
    date_range,
    report_open_items_move_line rlo
INNER JOIN
    report_open_items_partner rpo ON rlo.report_partner_id = rpo.id
INNER JOIN
    report_open_items_account rao ON rpo.report_account_id = rao.id
INNER JOIN
    report_aged_partner_balance_account ra ON rao.code = ra.code
INNER JOIN
    report_aged_partner_balance_partner rp
        ON
            ra.id = rp.report_account_id
        """.format(date_field=date_field)

        if not only_empty_partner_line:
            query_inject_line += """
        AND rpo.partner_id = rp.partner_id
            """
        elif only_empty_partner_line:
            query_inject_line += """
        AND rpo.partner_id IS NULL
        AND rp.partner_id IS NULL
            """
        query_inject_line += """
WHERE
    rao.report_id = %s
AND ra.report_id = %s
GROUP BY
    rp.id
        """

        # Prepare parameters (Identical to original method)
        query_inject_line_params = (self.date_at,) * 5
        query_inject_line_params += (
            self.env.uid,
            self.open_items_id.id,
            self.id,
        )
        self.env.cr.execute(query_inject_line, query_inject_line_params)