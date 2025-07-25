# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    invoice_per_delivery = fields.Boolean(
        string="Invoicing per delivery",
    )

    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ["invoice_per_delivery"]
