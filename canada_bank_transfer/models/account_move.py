# © 2021 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _constrains_date_sequence(self):
        pass
