# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    is_closing = fields.Boolean("Is Closing Journal")
