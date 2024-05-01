# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Account(models.Model):

    _inherit = "account.account"

    analytic_account_required = fields.Boolean()
    analytic_account_forbidden = fields.Boolean()

    @api.constrains("analytic_account_required", "analytic_account_forbidden")
    def _check_analytic_account_required_forbidden(self):
        for account in self:
            if account.analytic_account_required and account.analytic_account_forbidden:
                raise ValidationError(
                    _(
                        "The analytic account can not be required and forbidden "
                        "for the same GL account ({})."
                    ).format(self.display_name)
                )


def _format_account_move_line(move_line: "AccountMoveLine") -> str:
    """Format an account move line for displaying in a message error."""
    return "{} - {}".format(move_line.account_id.code, move_line.name)


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _check_analytic_account_required_or_forbidden(self):
        if not self.analytic_account_id and self.account_id.analytic_account_required:
            raise ValidationError(
                _(
                    "The journal entry can not be posted because the line {line} "
                    "has no analytic account. The account {account} requires "
                    "an analytic account."
                ).format(
                    line=_format_account_move_line(self),
                    account=self.account_id.display_name,
                )
            )

        if self.analytic_account_id and self.account_id.analytic_account_forbidden:
            raise ValidationError(
                _(
                    "The journal entry can not be posted because the line {line} "
                    "has an analytic account ({analytic_account}). "
                    "The account {account} forbids an analytic account."
                ).format(
                    line=_format_account_move_line(self),
                    account=self.account_id.display_name,
                    analytic_account=self.analytic_account_id.display_name,
                )
            )


class AccountMove(models.Model):

    _inherit = "account.move"

    def _check_analytic_account_required_or_forbidden(self):
        for line in self.mapped("line_ids"):
            line._check_analytic_account_required_or_forbidden()

    def _post(self, *args, **kwargs):
        self._check_analytic_account_required_or_forbidden()
        return super()._post(*args, **kwargs)
