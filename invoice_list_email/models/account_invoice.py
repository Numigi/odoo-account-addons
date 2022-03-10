# © 2021 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    partner_email = fields.Char(related="partner_id.email")
