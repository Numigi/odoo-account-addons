# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class AccountClosingWizard(models.TransientModel):

    _name = "account.closing.wizard"
    _description = "Account Closing Wizard"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    journal_id = fields.Many2one(
        "account.journal",
        required=True,
        default=lambda self: self._get_default_journal_id(),
    )

    date_range_id = fields.Many2one("date.range", "Date Range")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    move_id = fields.Many2one("account.move")

    def _check_draft_account_move_in_period(self):
        domain = [("state", "=", "draft"), ("move_type", "=", "entry"),
                  ("company_id", "=", self.env.user.company_id.id),
                  ("date", "<=", self.date_to)]
        account_ids = self.env["account.move"].search(domain)
        if account_ids:
            raise ValidationError(
                _(
                    "There are Draft Account Moves for that period. "
                    "To close a Period, No Draft Moves should be recorded "
                    "For The Period. "
                )
            )

    @api.model
    def _get_default_journal_id(self):
        return self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.user.company_id.id),
                ("is_closing", "=", True),
            ],
            limit=1,
        )

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def confirm(self):
        self._check_draft_account_move_in_period()
        self.move_id = self._make_account_move()
        return self.move_id.get_formview_action()

    def _make_account_move(self):
        income_lines = self._prepare_income_lines()
        earnings_line = self._prepare_earnings_line()

        balance = sum(l["debit"] - l["credit"] for l in income_lines)
        earnings_line["debit"] = -balance if balance < 0 else 0
        earnings_line["credit"] = balance if balance > 0 else 0

        lines = [
            earnings_line,
            *income_lines,
        ]
        return self.env["account.move"].create(
            {
                "date": self.date_to,
                "ref": self._get_account_move_ref(),
                "journal_id": self.journal_id.id,
                "company_id": self.company_id.id,
                "line_ids": [(0, 0, vals) for vals in reversed(lines)],
            }
        )

    def _get_account_move_ref(self):
        date_from = self.date_from.strftime(DATE_FORMAT)
        date_to = self.date_to.strftime(DATE_FORMAT)
        return _("Period closing from {date_from} to {date_to}").format(
            date_from=date_from, date_to=date_to,
        )

    def _prepare_earnings_line(self):
        return {
            "account_id": self._get_earnings_account().id,
            "name": "/",
        }

    def _get_earnings_account(self):
        account = self.env["account.account"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("is_default_earnings_account", "=", True),
            ],
            limit=1,
        )

        if not account:
            raise ValidationError(
                _(
                    "No account defined under company {company} "
                    "as the default account for retained earnings."
                ).format(company=self.company_id.display_name,)
            )

        return account

    def _prepare_income_lines(self):
        lines = (
            self._prepare_income_line(account)
            for account in self._get_income_accounts()
        )
        return [l for l in lines if l["debit"] or l["credit"]]

    def _prepare_income_line(self, account):
        balance = self._get_account_balance(account)
        return {
            "account_id": account.id,
            "debit": -balance if balance < 0 else 0,
            "credit": balance if balance > 0 else 0,
        }

    def _get_income_accounts(self):
        return self.env["account.account"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("internal_group", "in", ("expense", "income")),
            ],
            order="code",
        )

    def _get_account_balance(self, account):
        date_from = self.date_from.strftime(DATE_FORMAT)
        date_to = self.date_to.strftime(DATE_FORMAT)
        self._cr.execute(
            """
            SELECT aml.account_id, sum(aml.debit) - sum(aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date >= %s
            AND aml.date <= %s
            AND aml.account_id = %s
            and am.state = 'posted'
            GROUP BY aml.account_id
            """,
            (date_from, date_to, account.id),
        )
        res = self._cr.fetchall()
        return res[0][1] if res else 0
