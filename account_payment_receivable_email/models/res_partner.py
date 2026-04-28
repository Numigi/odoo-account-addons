# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_receivable_account = fields.Boolean(
        string="Is Receivable Account",
        default=False,
        copy=False,
    )

    payment_email_id = fields.Many2one(
        'res.partner',
        string="Receivable Accounts Contact",
        domain="[('is_receivable_account', '=', True)]",
        help="Select the specific contact to receive payment notifications."
    )
