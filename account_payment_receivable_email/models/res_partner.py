# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    payment_email = fields.Char(
        string="Receivable Accounts Email",
        help="Email address to send payment notifications and receipts",
    )