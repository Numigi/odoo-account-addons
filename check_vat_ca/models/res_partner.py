# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # VAT validation in Canada
    def check_vat_ca(self, vat):
        """Always accept the vat for Canada"""
        return True
