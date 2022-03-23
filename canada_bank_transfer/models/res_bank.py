# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Bank(models.Model):

    _inherit = "res.bank"

    canada_institution = fields.Char(size=3, string="Institution Number")

    @api.constrains("canada_institution")
    def _check_canada_institution_is_3_digits(self):
        banks_with_institution = self.filtered(lambda b: b.canada_institution)
        for bank in banks_with_institution:
            if not bank.canada_institution.isdigit() or len(bank.canada_institution) != 3:
                raise ValidationError(
                    _("The institution number must contain 3 digits. Got `{}`.").format(
                        bank.canada_institution
                    )
                )
