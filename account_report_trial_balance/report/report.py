# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class TrialBalanceReport(models.TransientModel):

    _name = "account.report.trial.balance"
    _description = "Trial Balance Report"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.user.company_id
    )

    date_range_id = fields.Many2one("date.range", "Date Range")

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    exclude_null = fields.Boolean(string="Exclude Accounts At Zero")

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def get_html(self):
        rendering_variables = self.get_rendering_variables()
        return self.env.ref(
            "account_report_trial_balance.trial_balance_report_html"
        ).render(rendering_variables)

    def get_pdf(self):
        base_url = self._get_report_url()
        rendering_variables = self.get_rendering_variables()
        rendering_variables.update({"mode": "print", "base_url": base_url})
        body = self.env["ir.ui.view"].render_template(
            "account_report_trial_balance.trial_balance_report_pdf",
            values=rendering_variables,
        )
        header = self.env["ir.actions.report"].render_template(
            "web.minimal_layout", values=rendering_variables
        )
        return self.env["ir.actions.report"]._run_wkhtmltopdf(
            [body],
            header=header,
            landscape=True,
            specific_paperformat_args={
                "data-report-margin-top": 10,
                "data-report-header-spacing": 10,
            },
        )

    def _get_report_url(self):
        config = self.env['ir.config_parameter'].sudo()
        return config.get_param('report.url') or config.get_param('web.base.url')

    def get_rendering_variables(self):
        return {
            "report": self,
            "lines": self._get_lines(),
        }

    def validate(self):
        action = self.env.ref("account_report_trial_balance.report_action").read()[0]
        action["res_id"] = self.id
        return action

    def initial_balance_clicked(self, account_id):
        action = self._get_move_line_action()
        account = self._get_account(account_id)
        action["name"] = _("({account}) - Initial Balance").format(account=account.display_name)
        action["domain"] = self._get_initial_balance_domain(account_id)
        return action

    def debit_clicked(self, account_id):
        action = self._get_move_line_action()
        account = self._get_account(account_id)
        action["name"] = _("({account}) - Debit").format(account=account.display_name)
        action["domain"] = self._get_period_domain(account_id)
        return action

    def credit_clicked(self, account_id):
        action = self._get_move_line_action()
        account = self._get_account(account_id)
        action["name"] = _("({account}) - Credit").format(account=account.display_name)
        action["domain"] = self._get_period_domain(account_id)
        return action

    def balance_clicked(self, account_id):
        action = self._get_move_line_action()
        account = self._get_account(account_id)
        action["name"] = _("({account}) - Balance").format(account=account.display_name)
        action["domain"] = self._get_period_domain(account_id)
        return action

    def closing_balance_clicked(self, account_id):
        action = self._get_move_line_action()
        account = self._get_account(account_id)
        action["name"] = _("({account}) - Closing Balance").format(account=account.display_name)
        action["domain"] = self._get_closing_balance_domain(account_id)
        return action

    def _get_initial_balance_domain(self, account_id):
        return [
            ("account_id", "=", account_id),
            ("date", "<", self.date_from),
            ("move_id.state", "=", "posted"),
        ]

    def _get_period_domain(self, account_id):
        return [
            ("account_id", "=", account_id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("move_id.state", "=", "posted"),
        ]

    def _get_closing_balance_domain(self, account_id):
        return [
            ("account_id", "=", account_id),
            ("date", "<=", self.date_to),
            ("move_id.state", "=", "posted"),
        ]

    def _get_account(self, account_id):
        return self.env["account.account"].browse(account_id)

    def _get_move_line_action(self):
        return {
            "res_model": "account.move.line",
            "views": [[False, "list"], [False, "form"]],
            "type": "ir.actions.act_window",
            "target": "current",
        }

    def _get_lines(self):
        return [self._get_account_line(account) for account in self._get_accounts()]

    def _get_account_line(self, account):
        debit, credit = self._get_debit_credit(account)
        balance = debit - credit
        initial_balance = self._initial_balance(account)
        return {
            "account": account,
            "debit": debit,
            "credit": credit,
            "balance": balance,
            "initial_balance": initial_balance,
            "closing_balance": initial_balance + balance,
        }

    def _get_accounts(self):
        domain = self._get_account_domain()
        accounts = self.env["account.account"].search(domain)
        if self.exclude_null:
            accounts = self._filter_null_accounts(accounts)

        return accounts

    def _get_account_domain(self):
        return [
            ("company_id", "=", self.company_id.id),
        ]

    def _filter_null_accounts(self, accounts):
        return accounts.filtered(lambda r: self._get_debit_credit(r) != (0,0) or self._initial_balance(r))

    def _get_debit_credit(self, account):
        date_from = self.date_from.strftime(DATE_FORMAT)
        date_to = self.date_to.strftime(DATE_FORMAT)
        self._cr.execute(
            """
            SELECT aml.account_id, sum(aml.debit), sum(aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date >= %s
            AND aml.date <= %s
            AND aml.account_id = %s
            and am.state = 'posted'
            GROUP BY aml.account_id
            """,
            (date_from, date_to, account.id,),
        )
        res = self._cr.fetchall()
        if not res:
            return 0, 0

        return res[0][1], res[0][2]

    def _initial_balance(self, account):
        date_from = self.date_from.strftime(DATE_FORMAT)
        self._cr.execute(
            """
            SELECT aml.account_id, sum(aml.debit) - sum(aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date < %s
            AND aml.account_id = %s
            and am.state = 'posted'
            GROUP BY aml.account_id
            """,
            (date_from, account.id,),
        )
        res = self._cr.fetchall()
        if not res:
            return 0

        return res[0][1]
