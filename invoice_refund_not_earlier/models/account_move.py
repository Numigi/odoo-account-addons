# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):

    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        for i, move in enumerate(self):
            date = default_values_list[i].get("date")
            if date and date < move.date:
                raise ValidationError(_(
                    "The date of the reversal entry ({reversal_date}) "
                    "can not be prior to the original move date ({move_date})."
                ).format(reversal_date=date, move_date=move.date))
        return super()._reverse_moves(default_values_list, cancel)
