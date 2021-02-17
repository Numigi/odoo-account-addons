# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Account(models.Model):

    _inherit = "account.account"

    is_default_earnings_account = fields.Boolean(
        "Default Retained Earnings Account", copy=False
    )

    @api.constrains("company_id", "is_default_earnings_account")
    def _check_single_default_earnings_account(self):
        for account in self.filtered("is_default_earnings_account"):
            other_account = self.sudo().search(
                [
                    ("company_id", "=", account.company_id.id),
                    ("is_default_earnings_account", "=", True),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )
            if other_account:
                raise ValidationError(
                    _(
                        "The account {} is already defined as default account for "
                        "retained earnings. "
                        "You may only define one default retained earnings account per company."
                    ).format(other_account.display_name)
                )
