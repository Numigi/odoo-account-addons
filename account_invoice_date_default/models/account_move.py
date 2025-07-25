# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _default_invoice_date(self):
        move_type = self.default_get(["move_type"])["move_type"]
        return fields.Date.context_today(self) if move_type == "in_invoice" else False

    invoice_date = fields.Date(default=_default_invoice_date)
