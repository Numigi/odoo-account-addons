# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    canada_transit = fields.Char(size=5, string="Transit Number")

    @api.constrains("canada_transit")
    def _check_canada_transit_is_5_digits(self):
        accounts_with_transit = self.filtered(lambda b: b.canada_transit)
        for account in accounts_with_transit:
            if not account.canada_transit.isdigit() or len(account.canada_transit) != 5:
                raise ValidationError(
                    _("The transit number must contain 5 digits. Got `{}`.").format(
                        account.canada_transit
                    )
                )

    @property
    def formatted_canada_number(self):
        return "{transit} {institution} {account_number}".format(
            transit=self.canada_transit or "XXXXX",
            institution=self.bank_id.canada_institution or "XXX",
            account_number=self.acc_number,
        )

    @api.multi
    def name_get(self):
        """Format the displayed name of canada accounts with the extra fields.

        The transit and institution number are added.

        If the transit or the institution number is missing, replace the number
        with a series of `X`. This allows to easily identify what field is missing.
        """
        canada_accounts = self.filtered(
            lambda a: a.canada_transit or a.bank_id.canada_institution
        )
        canada_accounts_result = [
            (a.id, a.formatted_canada_number) for a in canada_accounts
        ]

        other_accounts = self - canada_accounts
        other_accounts_result = super(ResPartnerBank, other_accounts).name_get()

        return canada_accounts_result + other_accounts_result

    @api.depends("acc_number")
    def _compute_sanitized_acc_number(self):
        """Add canada parts to the field sanitized_acc_number.

        This prevents the unique constraint from failling on sanitized_acc_number
        if 2 accounts with different transits have the same number.
        """
        canada_accounts = self.filtered(lambda a: a.canada_transit)
        for account in canada_accounts:
            account.sanitized_acc_number = account.formatted_canada_number

        other_accounts = self - canada_accounts
        super(ResPartnerBank, other_accounts)._compute_sanitized_acc_number()
